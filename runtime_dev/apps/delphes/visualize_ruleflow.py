#!/usr/bin/env python3
"""
Visualisation hiérarchique du ruleflow du moteur de décision Delphes.
Affiche l'arborescence des packages de règles et l'ordre d'exécution.
"""

import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple


class RuleFlowVisualizer:
    """Analyse et visualise la structure du ruleflow"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.ruleflow_function = None
        
    def parse_file(self):
        """Parse le fichier Python et extrait la fonction ruleflow"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.tree = ast.parse(content)
        
        # Trouver la fonction ruleflow
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'ruleflow':
                self.ruleflow_function = node
                break
                
    def extract_packages_and_rules(self) -> List[Tuple[str, List[str]]]:
        """Extrait les packages de règles et leurs règles"""
        if not self.ruleflow_function:
            return []
        
        packages = []
        
        # Parcourir le corps de ruleflow
        for stmt in self.ruleflow_function.body:
            # Chercher les définitions de fonctions (packages)
            if isinstance(stmt, ast.FunctionDef) and stmt.name.startswith('package_'):
                package_name = stmt.name
                rules = []
                
                # Extraire les règles de ce package
                for package_stmt in stmt.body:
                    if isinstance(package_stmt, ast.FunctionDef) and package_stmt.name.startswith('rule_'):
                        rules.append(package_stmt.name)
                
                packages.append((package_name, rules))
        
        return packages
    
    def extract_execution_order(self) -> List[str]:
        """Extrait l'ordre d'exécution des packages"""
        if not self.ruleflow_function:
            return []
        
        execution_order = []
        
        # Chercher les appels de fonctions à la fin de ruleflow
        for stmt in self.ruleflow_function.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name):
                    execution_order.append(stmt.value.func.id)
            elif isinstance(stmt, ast.If):
                # Gérer les appels conditionnels
                for if_stmt in stmt.body:
                    if isinstance(if_stmt, ast.Expr) and isinstance(if_stmt.value, ast.Call):
                        if isinstance(if_stmt.value.func, ast.Name):
                            func_name = if_stmt.value.func.id
                            # Extraire la condition
                            condition = ast.unparse(stmt.test) if hasattr(ast, 'unparse') else "condition"
                            execution_order.append(f"{func_name} [if {condition}]")
        
        return execution_order
    
    def print_tree_structure(self):
        """Affiche l'arborescence hiérarchique complète"""
        packages = self.extract_packages_and_rules()
        execution_order = self.extract_execution_order()
        
        # En-tête
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "RULEFLOW - MOTEUR DE DÉCISION DELPHES" + " " * 20 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        
        # Structure hiérarchique
        print("┌─ 📋 STRUCTURE HIÉRARCHIQUE DES RÈGLES")
        print("│")
        
        for i, (package_name, rules) in enumerate(packages):
            is_last_package = (i == len(packages) - 1)
            package_connector = "└──" if is_last_package else "├──"
            
            # Nom du package avec emoji
            package_display = package_name.replace("package_", "").replace("_", " ").title()
            print(f"│   {package_connector} 📦 {package_display}")
            print(f"│   {'    ' if is_last_package else '│   '}    ({package_name})")
            print(f"│   {'    ' if is_last_package else '│   '}")
            
            # Liste des règles
            for j, rule in enumerate(rules):
                is_last_rule = (j == len(rules) - 1)
                rule_connector = "└──" if is_last_rule else "├──"
                indent = "    " if is_last_package else "│   "
                sub_indent = "    " if is_last_rule else "│   "
                
                rule_display = rule.replace("rule_", "").replace("_", " ").capitalize()
                print(f"│   {indent}    {rule_connector} ⚙️  {rule_display}")
                print(f"│   {indent}    {sub_indent}   ({rule})")
                
                if not is_last_rule:
                    print(f"│   {indent}    │")
            
            if not is_last_package:
                print("│   │")
        
        print("│")
        print("└" + "─" * 78)
        print()
        
        # Ordre d'exécution
        print("┌─ 🔄 ORDRE D'EXÉCUTION DES PACKAGES")
        print("│")
        
        for i, package in enumerate(execution_order, 1):
            print(f"│   {i}. {package}")
        
        print("│")
        print("└" + "─" * 78)
        print()
        
        # Statistiques
        total_rules = sum(len(rules) for _, rules in packages)
        print("┌─ 📊 STATISTIQUES")
        print("│")
        print(f"│   • Nombre de packages : {len(packages)}")
        print(f"│   • Nombre total de règles : {total_rules}")
        print(f"│   • Nombre d'étapes d'exécution : {len(execution_order)}")
        print("│")
        print("└" + "─" * 78)
        print()
    
    def generate_mermaid_diagram(self) -> str:
        """Génère un diagramme Mermaid du ruleflow"""
        packages = self.extract_packages_and_rules()
        execution_order = self.extract_execution_order()
        
        mermaid = ["```mermaid", "graph TD"]
        mermaid.append("    Start([🚀 Début du Ruleflow])")
        
        # Créer les nœuds pour chaque package
        for i, (package_name, rules) in enumerate(packages):
            package_id = f"P{i}"
            package_display = package_name.replace("package_", "").replace("_", " ").title()
            mermaid.append(f"    {package_id}[📦 {package_display}]")
            
            # Créer les nœuds pour chaque règle
            for j, rule in enumerate(rules):
                rule_id = f"P{i}R{j}"
                rule_display = rule.replace("rule_", "").replace("_", " ").capitalize()
                mermaid.append(f"    {rule_id}[⚙️ {rule_display}]")
        
        mermaid.append("    End([🏁 Fin du Ruleflow])")
        
        # Créer les connexions
        mermaid.append("")
        mermaid.append("    Start --> P0")
        
        for i, (package_name, rules) in enumerate(packages):
            package_id = f"P{i}"
            
            # Connexions package -> règles
            for j, rule in enumerate(rules):
                rule_id = f"P{i}R{j}"
                mermaid.append(f"    {package_id} --> {rule_id}")
            
            # Connexion vers le package suivant
            if i < len(packages) - 1:
                next_package_id = f"P{i+1}"
                mermaid.append(f"    {package_id} --> {next_package_id}")
            else:
                mermaid.append(f"    {package_id} --> End")
        
        mermaid.append("```")
        
        return "\n".join(mermaid)


def main():
    """Point d'entrée principal"""
    # Chemin vers le fichier decision_engine.py
    script_dir = Path(__file__).parent
    decision_engine_path = script_dir / "decision_engine.py"
    
    if not decision_engine_path.exists():
        print(f"❌ Erreur : Le fichier {decision_engine_path} n'existe pas.")
        sys.exit(1)
    
    # Créer le visualiseur et parser le fichier
    visualizer = RuleFlowVisualizer(str(decision_engine_path))
    visualizer.parse_file()
    
    if not visualizer.ruleflow_function:
        print("❌ Erreur : La fonction 'ruleflow' n'a pas été trouvée.")
        sys.exit(1)
    
    # Afficher la structure hiérarchique
    visualizer.print_tree_structure()
    
    # Générer et afficher le diagramme Mermaid
    print("┌─ 📐 DIAGRAMME MERMAID")
    print("│")
    print("│   Copiez le code ci-dessous dans un éditeur Markdown compatible Mermaid")
    print("│   (GitHub, GitLab, VS Code avec extension, etc.)")
    print("│")
    print("└" + "─" * 78)
    print()
    print(visualizer.generate_mermaid_diagram())
    print()


if __name__ == "__main__":
    main()
