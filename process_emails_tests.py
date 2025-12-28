#!/usr/bin/env python3
"""
Script pour traiter le fichier Excel "Emails type.xlsx", exécuter des tests d'analyse
et ajouter les résultats dans une nouvelle colonne avec la date.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import Optional
import requests
from src.common.config import SupportedLocale
from src.common.constants import API_ROUTE_V2


def check_backend_health(api_base_url: str) -> bool:
    """Vérifie que le backend est accessible"""
    health_url = f"{api_base_url}/api/health"
    try:
        response = requests.get(health_url, timeout=5.0)
        return response.status_code == 200
    except:
        return False


def analyze_text(
    api_base_url: str,
    app_id: str,
    locale: SupportedLocale,
    text: str,
    field_values: dict,
    read_from_cache: bool,
    llm_config_id: str
) -> dict:
    """
    Appelle l'API d'analyse
    
    Returns:
        dict: Résultat de l'analyse ou dict avec 'error' en cas d'erreur
    """
    url = f"{api_base_url}{API_ROUTE_V2}/apps/{app_id}/{locale}/analyze"
    
    payload = {
        "field_values": field_values,
        "text": text,
        "read_from_cache": read_from_cache,
        "llm_config_id": llm_config_id
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60.0)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text[:200]  # Limiter la taille
            }
    except requests.exceptions.ConnectionError:
        return {"error": "connection_error", "message": "Backend inaccessible"}
    except requests.exceptions.Timeout:
        return {"error": "timeout", "message": "Timeout lors de l'appel"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)[:200]}


def is_date_column(column_name: str) -> bool:
    """
    Vérifie si une colonne est une date (format dd/MM/yyyy ou similaire)
    """
    if pd.isna(column_name):
        return False
    
    col_str = str(column_name).strip()
    # Vérifier si c'est un format de date commun
    date_patterns = [
        r'\d{2}/\d{2}/\d{4}',  # dd/MM/yyyy
        r'\d{4}-\d{2}-\d{2}',  # yyyy-MM-dd
        r'\d{2}-\d{2}-\d{4}',  # dd-MM-yyyy
    ]
    
    import re
    for pattern in date_patterns:
        if re.match(pattern, col_str):
            return True
    
    # Vérifier si le nom de colonne contient "date" ou "Date"
    if 'date' in col_str.lower():
        return True
    
    return False


def create_field_values(row: pd.Series, exclude_date_columns: bool = True, exclude_columns: Optional[list] = None) -> dict:
    """
    Crée un dictionnaire field_values à partir d'une ligne du DataFrame
    en excluant les colonnes de dates si demandé et les colonnes spécifiées
    
    Args:
        row: Ligne du DataFrame
        exclude_date_columns: Si True, exclut les colonnes de dates
        exclude_columns: Liste des noms de colonnes à exclure
    """
    if exclude_columns is None:
        exclude_columns = []
    
    field_values = {}
    
    # Date d'aujourd'hui au format dd/MM/yyyy
    date_demande = datetime.now().strftime("%d/%m/%Y")
    field_values["date_demande"] = date_demande
    
    # Parcourir toutes les colonnes
    for col in row.index:
        # Exclure les colonnes de dates si demandé
        if exclude_date_columns and is_date_column(col):
            continue
        
        # Exclure les colonnes spécifiées
        if str(col) in exclude_columns:
            continue
        
        value = row[col]
        
        # Ignorer les valeurs NaN
        if pd.isna(value):
            continue
        
        # Convertir en string et nettoyer
        value_str = str(value).strip()
        if value_str and value_str.lower() != 'nan':
            # Utiliser le nom de colonne en minuscules avec underscores
            key = str(col).lower().replace(' ', '_').replace('/', '_')
            field_values[key] = value_str
    
    return field_values


def process_excel_file(
    input_file: str = "Emails type.xlsx",
    output_file: Optional[str] = None,
    api_base_url: str = "http://localhost:8002",
    app_id: str = "delphes78",
    locale: SupportedLocale = "fr",
    llm_config_id: str = "scaleway1"
):
    """
    Traite le fichier Excel, exécute les tests et ajoute les résultats
    """
    if output_file is None:
        output_file = input_file
    
    print("=" * 60)
    print("Traitement du fichier Excel")
    print("=" * 60)
    print(f"Fichier d'entrée: {input_file}")
    print(f"Fichier de sortie: {output_file}")
    
    # Vérifier que le backend est accessible
    print("\nVérification du backend...")
    if not check_backend_health(api_base_url):
        print("✗ Le backend n'est pas accessible. Arrêt du traitement.")
        return
    print("✓ Backend accessible")
    
    # Lire le fichier Excel
    print(f"\nLecture du fichier {input_file}...")
    try:
        df = pd.read_excel(input_file)
        print(f"✓ Fichier lu: {len(df)} lignes, {len(df.columns)} colonnes")
    except Exception as e:
        print(f"✗ Erreur lors de la lecture: {e}")
        return
    
    # Identifier les colonnes de dates à exclure
    date_columns = [col for col in df.columns if is_date_column(col)]
    if date_columns:
        print(f"\nColonnes de dates détectées (seront exclues des payloads): {date_columns}")
    
    # Créer le nom de la nouvelle colonne avec la date actuelle
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    result_column = timestamp
    
    # Vérifier si cette colonne existe déjà
    if result_column in df.columns:
        print(f"\n⚠️  La colonne '{result_column}' existe déjà. Les résultats seront mis à jour.")
    else:
        print(f"\nCrée la colonne de résultats: '{result_column}'")
        df[result_column] = None
    
    # Colonne pour le texte à analyser
    text_column = "Texte Mail"
    if text_column not in df.columns:
        print(f"✗ Colonne '{text_column}' introuvable. Colonnes disponibles: {list(df.columns)}")
        return
    
    # Traiter chaque ligne
    print(f"\nTraitement de {len(df)} lignes...")
    print("-" * 60)
    
    for idx, row in df.iterrows():
        text = row[text_column]
        
        # Ignorer les lignes sans texte
        text_str = str(text) if not pd.isna(text) else ''
        if not text_str.strip():
            print(f"Ligne {int(idx) + 1}: ⚠️  Pas de texte, ignorée")
            continue
        
        print(f"Ligne {int(idx) + 1}/{len(df)}: Traitement en cours...", end=' ', flush=True)
        
        # Créer le payload (exclure les colonnes de dates et "Type de problème")
        exclude_cols = ["Type de problème"]
        field_values = create_field_values(row, exclude_date_columns=True, exclude_columns=exclude_cols)
        
        # Appeler l'API
        result = analyze_text(
            api_base_url=api_base_url,
            app_id=app_id,
            locale=locale,
            text=text_str,
            field_values=field_values,
            read_from_cache=False,
            llm_config_id=llm_config_id
        )
        
        # Stocker le résultat
        if "error" in result:
            result_str = f"ERREUR: {result.get('error', 'unknown')} - {result.get('message', '')}"
            print(f"✗ {result_str}")
        else:
            # Extraire l'intention principale (celle avec le score le plus élevé)
            if "analysis_result" in result and "scorings" in result["analysis_result"]:
                scorings = result["analysis_result"]["scorings"]
                if scorings:
                    top_intention = max(scorings, key=lambda x: x.get("score", 0))
                    intention_label = top_intention.get("intention_label", "N/A")
                    score = top_intention.get("score", 0)
                    result_str = f"Intention: {intention_label} (Score: {score})"
                else:
                    result_str = "Aucune intention trouvée"
            else:
                result_str = "Résultat inattendu"
            print(f"✓ {result_str}")
        
        # Stocker le résultat dans le DataFrame
        df.at[idx, result_column] = result_str
        
        # Sauvegarder après chaque ligne pour ne pas perdre les résultats
        try:
            df.to_excel(output_file, index=False)
        except Exception as e:
            print(f"\n⚠️  Erreur lors de la sauvegarde: {e}")
    
    # Sauvegarde finale
    print("\n" + "-" * 60)
    print(f"Sauvegarde finale dans {output_file}...")
    try:
        df.to_excel(output_file, index=False)
        print(f"✓ Fichier sauvegardé avec succès")
    except Exception as e:
        print(f"✗ Erreur lors de la sauvegarde finale: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Traitement terminé")
    print("=" * 60)


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Traite un fichier Excel et exécute des tests d'analyse")
    parser.add_argument("--input", default="Emails type.xlsx", help="Fichier Excel d'entrée")
    parser.add_argument("--output", default=None, help="Fichier Excel de sortie (par défaut: même que l'entrée)")
    parser.add_argument("--api-url", default="http://localhost:8002", help="URL de l'API backend")
    parser.add_argument("--app-id", default="delphes78", help="ID de l'application")
    parser.add_argument("--locale", default="fr", help="Locale")
    parser.add_argument("--llm-config", default="scaleway1", help="Configuration LLM")
    
    args = parser.parse_args()
    
    process_excel_file(
        input_file=args.input,
        output_file=args.output,
        api_base_url=args.api_url,
        app_id=args.app_id,
        locale=args.locale,
        llm_config_id=args.llm_config
    )


if __name__ == "__main__":
    main()

