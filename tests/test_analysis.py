#!/usr/bin/env python
"""
Script de test pour le web service analysis
Teste l'appel à l'endpoint /api/v2/apps/{app_id}/{locale}/analyze
"""

import os
import sys
import json
from typing import Optional
from datetime import datetime
import requests

# Ajouter le répertoire parent au chemin pour accéder aux modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.common.config import SupportedLocale
from src.common.constants import API_ROUTE_V2


def get_llm_config_ids(api_base_url: str, app_id: str) -> list[str]:
    """
    Récupère la liste des configurations LLM disponibles pour une application
    
    Args:
        api_base_url: URL de base de l'API
        app_id: Identifiant de l'application
    
    Returns:
        list[str]: Liste des IDs de configurations LLM disponibles, ou liste vide en cas d'erreur
    """
    url = f"{api_base_url}{API_ROUTE_V2}/apps/{app_id}/llm_config_ids"
    
    try:
        response = requests.get(url, timeout=5.0)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Impossible de récupérer les configurations LLM (code: {response.status_code})")
            return []
    except Exception as e:
        print(f"⚠️  Erreur lors de la récupération des configurations LLM: {type(e).__name__}")
        return []


def get_available_apps(api_base_url: str) -> list[str]:
    """
    Récupère la liste des applications disponibles
    
    Args:
        api_base_url: URL de base de l'API
    
    Returns:
        list[str]: Liste des IDs d'applications disponibles, ou liste vide en cas d'erreur
    """
    url = f"{api_base_url}{API_ROUTE_V2}/app_ids"
    
    try:
        response = requests.get(url, timeout=5.0)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Impossible de récupérer la liste des applications (code: {response.status_code})")
            return []
    except Exception as e:
        print(f"⚠️  Erreur lors de la récupération des applications: {type(e).__name__}")
        return []


def check_backend_health(api_base_url: str) -> bool:
    """
    Vérifie que le backend est accessible en testant l'endpoint /api/health
    
    Args:
        api_base_url: URL de base de l'API
    
    Returns:
        bool: True si le backend est accessible, False sinon
    """
    health_url = f"{api_base_url}/api/health"
    
    try:
        response = requests.get(health_url, timeout=5.0)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ Backend accessible: {health_data.get('service', 'unknown')}")
            return True
        else:
            print(f"✗ Backend répond avec un code d'erreur: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Backend inaccessible à {api_base_url}")
        print("   Le serveur backend ne répond pas.")
        print("   Vérifiez que le backend est démarré et écoute sur le bon port.")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Timeout lors de la vérification du backend à {api_base_url}")
        return False
    except Exception as e:
        print(f"✗ Erreur lors de la vérification du backend: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        return False


def test_analyze(
    api_base_url: str = "http://localhost:8002",
    app_id: str = "delphes",
    locale: SupportedLocale = "fr",
    text: str = "Je souhaite renouveler mon titre de séjour",
    field_values: Optional[dict] = None,
    read_from_cache: bool = False,
    llm_config_id: str = "default"
) -> dict:
    """
    Teste l'appel au web service analysis
    
    Args:
        api_base_url: URL de base de l'API (défaut: http://localhost:8002)
        app_id: Identifiant de l'application (défaut: delphes)
        locale: Locale (défaut: fr)
        text: Texte à analyser
        field_values: Valeurs des champs (défaut: {})
        read_from_cache: Utiliser le cache (défaut: False)
        llm_config_id: ID de configuration LLM (défaut: default)
    
    Returns:
        dict: Réponse de l'API
    """
    if field_values is None:
        field_values = {}
    
    print("=" * 60)
    print("Test du web service analysis")
    print("=" * 60)
    
    # Vérification préalable de l'accessibilité du backend
    print("\nVérification de l'accessibilité du backend...")
    if not check_backend_health(api_base_url):
        print("\n⚠️  Le backend n'est pas accessible. Le test ne peut pas continuer.")
        print("   Veuillez démarrer le backend avant de relancer le test.")
        return {"error": "backend_unavailable"}
    
    # Vérification que l'application existe
    print("\nVérification de l'application...")
    available_apps = get_available_apps(api_base_url)
    if available_apps and app_id not in available_apps:
        print(f"✗ L'application '{app_id}' n'existe pas.")
        print(f"\nApplications disponibles: {', '.join(available_apps)}")
        print(f"\n💡 Suggestion: Utilisez une des applications disponibles, par exemple:")
        print(f"   python -m tests.test_analysis {available_apps[0]} {locale} '{text}'")
        return {"error": "app_not_found", "available_apps": available_apps}
    elif available_apps:
        print(f"✓ Application '{app_id}' trouvée")
    
    # Vérification que la configuration LLM existe
    print("\nVérification de la configuration LLM...")
    available_llm_configs = get_llm_config_ids(api_base_url, app_id)
    if available_llm_configs and llm_config_id not in available_llm_configs:
        print(f"✗ La configuration LLM '{llm_config_id}' n'existe pas pour l'application '{app_id}'.")
        print(f"\nConfigurations LLM disponibles: {', '.join(available_llm_configs)}")
        # Utiliser la première configuration disponible ou "scaleway1" si disponible
        suggested_config = "scaleway1" if "scaleway1" in available_llm_configs else available_llm_configs[0] if available_llm_configs else None
        if suggested_config:
            print(f"\n💡 Suggestion: Utilisez une des configurations disponibles, par exemple:")
            print(f"   python -m tests.test_analysis {app_id} {locale} '{text}' --llm-config {suggested_config}")
            # Utiliser automatiquement la configuration suggérée
            llm_config_id = suggested_config
            print(f"   → Utilisation automatique de '{llm_config_id}'")
        else:
            return {"error": "llm_config_not_found", "available_configs": available_llm_configs}
    elif available_llm_configs:
        print(f"✓ Configuration LLM '{llm_config_id}' trouvée")
    
    # Construction de l'URL et du payload après les vérifications
    url = f"{api_base_url}{API_ROUTE_V2}/apps/{app_id}/{locale}/analyze"
    
    payload = {
        "field_values": field_values,
        "text": text,
        "read_from_cache": read_from_cache,
        "llm_config_id": llm_config_id
    }
    
    print(f"\nURL: {url}")
    print(f"App ID: {app_id}")
    print(f"Locale: {locale}")
    print(f"Text: {text}")
    print(f"Field values: {json.dumps(field_values, indent=2, ensure_ascii=False)}")
    print(f"Read from cache: {read_from_cache}")
    print(f"LLM Config ID: {llm_config_id}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=30.0)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Succès!")
            print("\nRéponse:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"✗ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text}")
            # Essayer de parser le JSON d'erreur si disponible
            try:
                error_json = response.json()
                if isinstance(error_json, dict) and "detail" in error_json:
                    print(f"Détails: {error_json['detail']}")
            except:
                pass
            return {"error": response.status_code, "message": response.text}
            
    except requests.exceptions.ConnectionError:
        print("✗ Erreur de connexion")
        print(f"Impossible de se connecter à {url}")
        print("Le backend était accessible au health check mais ne répond plus.")
        print("Vérifiez que le serveur backend est toujours démarré.")
        return {"error": "connection_error"}
    except requests.exceptions.Timeout:
        print("✗ Timeout")
        print("La requête a pris trop de temps.")
        return {"error": "timeout"}
    except Exception as e:
        print(f"✗ Erreur inattendue: {type(e).__name__}")
        print(f"Message: {str(e)}")
        return {"error": str(e)}


def main():
    """Fonction principale"""
    # Récupération des paramètres depuis les variables d'environnement ou arguments
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8002")
    
    # Paramètres par défaut
    # Note: on essaie de récupérer une app disponible, sinon on utilise "delphes78"
    app_id = "delphes78"  # Application par défaut
    locale = "fr"
    text = "Je souhaite renouveler mon titre de séjour"
    # Date d'aujourd'hui au format dd/MM/yyyy
    date_demande = datetime.now().strftime("%d/%m/%Y")
    field_values = {
        "date_demande": date_demande
    }
    read_from_cache = False
    llm_config_id = "scaleway1"  # Configuration LLM par défaut
    
    # Gestion des arguments en ligne de commande
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python -m tests.test_analysis [app_id] [locale] [text] [--llm-config CONFIG_ID]")
            print("\nExemples:")
            print("  python -m tests.test_analysis")
            print("  python -m tests.test_analysis delphes78 fr 'Je veux renouveler mon titre'")
            print("  python -m tests.test_analysis delphes91 en 'I want to renew my permit' --llm-config scaleway1")
            print("\nVariables d'environnement:")
            print("  API_BASE_URL: URL de base de l'API (défaut: http://localhost:8002)")
            print("\nNote: Le script vérifie automatiquement les applications et configurations LLM disponibles.")
            sys.exit(0)
        
        # Parse les arguments positionnels et nommés
        positional_args = []
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--llm-config" and i + 1 < len(sys.argv):
                llm_config_id = sys.argv[i + 1]
                i += 2
            elif not arg.startswith("--"):
                positional_args.append(arg)
                i += 1
            else:
                i += 1
        
        # Assigner les arguments positionnels
        if len(positional_args) >= 1:
            app_id = positional_args[0]
        if len(positional_args) >= 2:
            locale = positional_args[1]
        if len(positional_args) >= 3:
            text = positional_args[2]
    
    # Exécution du test
    result = test_analyze(
        api_base_url=api_base_url,
        app_id=app_id,
        locale=locale,
        text=text,
        field_values=field_values,
        read_from_cache=read_from_cache,
        llm_config_id=llm_config_id
    )
    
    print("\n" + "=" * 60)
    
    # Code de sortie
    if "error" in result:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
