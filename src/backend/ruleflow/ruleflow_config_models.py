# Nouveaux modèles Pydantic pour le format pivot
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

class OutputAssignmentModel(BaseModel):
    attribute: str  # ex: "priority", "work_basket", "acknowledgement_to_requester"
    value: str     # ex: "HIGH", "work_basket_accueil", "#VISIT_PAGE,text,url"
    line_number: Optional[int] = None

class RuleConfigModel(BaseModel):
    id: str
    name: str
    code: str
    free_code: Optional[str] = None  # Code libre (logique métier, calculs, conditions)
    output_assignments: Optional[List[OutputAssignmentModel]] = []  # Paramètres output structurés
    condition: Optional[str] = None

class PackageConfigModel(BaseModel):
    id: str
    name: str
    condition: Optional[str] = None
    execution_order: int
    rules: List[RuleConfigModel]

class MetadataModel(BaseModel):
    app_name: str
    class_name: str
    created_at: str
    modified_at: str
    runtime: str

class RuleflowConfigModel(BaseModel):
    version: str = "1.0"
    metadata: MetadataModel
    imports: List[str]
    constants: List[str]
    helper_functions: List[str]
    packages: List[PackageConfigModel]

class GenerateFromConfigRequest(BaseModel):
    config: RuleflowConfigModel

# Générateur de code à partir du format pivot
class RuleflowConfigGenerator:
    """Générateur de code Python à partir d'une configuration ruleflow JSON"""
    
    def __init__(self):
        pass
    
    def generate_python_code(self, config: RuleflowConfigModel) -> str:
        """Génère le code Python complet à partir de la configuration"""
        
        lines = []
        
        # Imports
        for import_line in config.imports:
            lines.append(import_line)
        lines.append("")
        
        # Constants
        if config.constants:
            for constant in config.constants:
                lines.append(constant)
            lines.append("")
        
        # Helper functions
        if config.helper_functions:
            for helper_func in config.helper_functions:
                lines.append(helper_func)
            lines.append("")
        
        # Classe principale
        lines.append(f"class {config.metadata.class_name}(CaseHandlingDecisionEngine):")
        lines.append("")
        
        # Méthode decide
        lines.append("    def decide(self, case_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:")
        lines.append("        output = CaseHandlingDecisionOutput()")
        lines.append("        output.details = []")
        lines.append("")
        
        # Packages triés par execution_order
        sorted_packages = sorted(config.packages, key=lambda p: p.execution_order)
        
        for pkg in sorted_packages:
            # Condition du package
            if pkg.condition and pkg.condition.strip():
                lines.append(f"        # Package: {pkg.name}")
                lines.append(f"        if {pkg.condition}:")
                package_indent = "            "
            else:
                lines.append(f"        # Package: {pkg.name}")
                package_indent = "        "
            
            # Rules du package
            for rule in pkg.rules:
                lines.append(f"{package_indent}# Rule: {rule.name}")
                
                if rule.condition and rule.condition.strip():
                    lines.append(f"{package_indent}if {rule.condition}:")
                    rule_indent = package_indent + "    "
                else:
                    rule_indent = package_indent
                
                # Code de la rule (avec indentation correcte)
                rule_code_lines = rule.code.split('\n')
                for i, code_line in enumerate(rule_code_lines):
                    if i == 0:
                        # Première ligne : appliquer l'indentation de base
                        if code_line.strip():
                            lines.append(f"{rule_indent}{code_line.strip()}")
                    else:
                        # Lignes suivantes : préserver l'indentation relative
                        if code_line.strip():
                            # Calculer l'indentation relative de la ligne
                            original_indent = len(code_line) - len(code_line.lstrip())
                            # Appliquer l'indentation de base + indentation relative
                            lines.append(f"{rule_indent}{' ' * original_indent}{code_line.strip()}")
                        else:
                            lines.append("")
                
                lines.append("")
        
        # Return statement
        lines.append("        return output")
        
        return '\n'.join(lines)
    
    def save_to_file(self, config: RuleflowConfigModel, file_path: str) -> str:
        """Sauvegarde le code généré dans un fichier"""
        
        python_code = self.generate_python_code(config)
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Écrire le fichier
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        return python_code
    
    def validate_config(self, config: RuleflowConfigModel) -> List[str]:
        """Valide la configuration et retourne une liste d'erreurs"""
        errors = []
        
        # Vérifications de base
        if not config.metadata.app_name:
            errors.append("Le nom de l'application est requis")
        
        if not config.metadata.class_name:
            errors.append("Le nom de la classe est requis")
        
        if not config.packages:
            errors.append("Au moins un package est requis")
        
        # Vérifier les noms uniques des packages
        package_names = [pkg.name for pkg in config.packages]
        if len(package_names) != len(set(package_names)):
            errors.append("Les noms de packages doivent être uniques")
        
        # Vérifier chaque package
        for pkg in config.packages:
            if not pkg.name:
                errors.append(f"Le package avec l'ID {pkg.id} doit avoir un nom")
            
            # Vérifier les noms uniques des rules dans le package
            rule_names = [rule.name for rule in pkg.rules]
            if len(rule_names) != len(set(rule_names)):
                errors.append(f"Les noms de rules doivent être uniques dans le package {pkg.name}")
            
            for rule in pkg.rules:
                if not rule.name:
                    errors.append(f"La rule avec l'ID {rule.id} doit avoir un nom")
                if not rule.code.strip():
                    errors.append(f"La rule {rule.name} doit avoir du code")
        
        return errors