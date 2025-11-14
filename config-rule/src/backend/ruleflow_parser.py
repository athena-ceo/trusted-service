import ast
import re
from pathlib import Path
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
from enum import Enum

class NodeType(str, Enum):
    PACKAGE = "package"
    RULE = "rule"
    CONDITION = "condition"

@dataclass
class RuleNode:
    """Représente une règle dans le ruleflow"""
    name: str
    code: str
    condition: Optional[str] = None
    line_start: int = 0
    line_end: int = 0

@dataclass
class PackageNode:
    """Représente un package dans le ruleflow"""
    name: str
    rules: List[RuleNode] = field(default_factory=list)
    condition: Optional[str] = None
    line_start: int = 0
    line_end: int = 0
    execution_order: int = 0

@dataclass
class RuleflowStructure:
    """Structure complète du ruleflow"""
    imports: List[str] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    helper_functions: List[str] = field(default_factory=list)
    packages: List[PackageNode] = field(default_factory=list)
    class_name: str = ""
    ruleflow_function_start: int = 0
    ruleflow_function_end: int = 0
    class_start: int = 0
    class_end: int = 0

class RuleflowParser:
    """Parse un fichier decision_engine.py pour extraire la structure du ruleflow"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.source_lines: List[str] = []
        self.ast_tree: Optional[ast.AST] = None
        
    def parse(self) -> RuleflowStructure:
        """Parse le fichier et retourne la structure"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.source_lines = f.readlines()
        
        source_code = ''.join(self.source_lines)
        self.ast_tree = ast.parse(source_code, filename=str(self.file_path))
        
        structure = RuleflowStructure()
        structure.imports = self._extract_imports()
        structure.constants = self._extract_constants()
        structure.helper_functions = self._extract_helper_functions()
        
        # Trouver la fonction ruleflow
        ruleflow_func = self._find_ruleflow_function()
        if ruleflow_func:
            structure.ruleflow_function_start = ruleflow_func.lineno - 1
            structure.ruleflow_function_end = ruleflow_func.end_lineno
            structure.packages = self._extract_packages(ruleflow_func)
        
        # Trouver la classe DecisionEngine
        decision_engine_class = self._find_decision_engine_class()
        if decision_engine_class:
            structure.class_name = decision_engine_class.name
            structure.class_start = decision_engine_class.lineno - 1
            structure.class_end = decision_engine_class.end_lineno
        
        return structure
    
    def _extract_imports(self) -> List[str]:
        """Extrait les imports"""
        imports = []
        seen = set()
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line_num = node.lineno - 1
                if line_num < len(self.source_lines) and line_num not in seen:
                    imports.append(self.source_lines[line_num].strip())
                    seen.add(line_num)
        return sorted(set(imports))
    
    def _extract_constants(self) -> List[str]:
        """Extrait les constantes (variables en majuscules)"""
        constants = []
        seen = set()
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        line_num = node.lineno - 1
                        if line_num < len(self.source_lines) and line_num not in seen:
                            constants.append(self.source_lines[line_num].strip())
                            seen.add(line_num)
        return constants
    
    def _extract_helper_functions(self) -> List[str]:
        """Extrait les fonctions helper (hors ruleflow et classe)"""
        helpers = []
        ruleflow_names = {'ruleflow', 'visualize_ruleflow'}
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                if node.name not in ruleflow_names and not self._is_in_class(node):
                    start = node.lineno - 1
                    end = node.end_lineno
                    func_code = ''.join(self.source_lines[start:end])
                    helpers.append(func_code)
        
        return helpers
    
    def _is_in_class(self, node: ast.AST) -> bool:
        """Vérifie si un node est dans une classe"""
        # Parcourir l'AST pour trouver la classe parente
        class_nodes = [n for n in ast.walk(self.ast_tree) if isinstance(n, ast.ClassDef)]
        for class_node in class_nodes:
            for child in ast.walk(class_node):
                if child == node:
                    return True
        return False
    
    def _find_ruleflow_function(self) -> Optional[ast.FunctionDef]:
        """Trouve la fonction ruleflow"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == 'ruleflow':
                # Vérifier qu'elle n'est pas dans une classe
                if not self._is_in_class(node):
                    return node
        return None
    
    def _find_decision_engine_class(self) -> Optional[ast.ClassDef]:
        """Trouve la classe DecisionEngine"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                # Chercher une classe qui hérite de CaseHandlingDecisionEngine
                for base in node.bases:
                    if isinstance(base, ast.Name) and 'DecisionEngine' in base.id:
                        return node
                    elif isinstance(base, ast.Attribute):
                        if 'DecisionEngine' in base.attr:
                            return node
        # Si pas trouvé par l'héritage, chercher par nom de classe
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                if 'DecisionEngine' in node.name:
                    return node
        return None
    
    def _extract_packages(self, ruleflow_func: ast.FunctionDef) -> List[PackageNode]:
        """Extrait les packages de la fonction ruleflow"""
        package_defs = {}
        
        # Trouver les définitions de packages
        for node in ast.walk(ruleflow_func):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('package_'):
                package_defs[node.name] = node
        
        # Analyser le body de ruleflow pour trouver l'ordre d'exécution et les conditions
        execution_order = []
        self._extract_package_execution_order(ruleflow_func.body, execution_order)
        
        # Créer les PackageNodes
        packages = []
        for i, (pkg_name, condition) in enumerate(execution_order):
            pkg_def = package_defs.get(pkg_name)
            if pkg_def:
                package = PackageNode(
                    name=pkg_name,
                    condition=condition,
                    execution_order=i,
                    line_start=pkg_def.lineno - 1,
                    line_end=pkg_def.end_lineno
                )
                package.rules = self._extract_rules_from_package(pkg_def)
                packages.append(package)
        
        return packages
    
    def _extract_package_execution_order(self, body: List[ast.stmt], execution_order: List[tuple]):
        """Extrait l'ordre d'exécution des packages avec leurs conditions"""
        for stmt in body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id.startswith('package_'):
                    execution_order.append((stmt.value.func.id, None))
            elif isinstance(stmt, ast.If):
                # Extraire la condition
                condition_code = self._ast_to_code(stmt.test)
                for body_stmt in stmt.body:
                    if isinstance(body_stmt, ast.Expr) and isinstance(body_stmt.value, ast.Call):
                        if isinstance(body_stmt.value.func, ast.Name) and body_stmt.value.func.id.startswith('package_'):
                            execution_order.append((body_stmt.value.func.id, condition_code))
                    elif isinstance(body_stmt, ast.If):
                        self._extract_package_execution_order([body_stmt], execution_order)
    
    def _extract_rules_from_package(self, package_func: ast.FunctionDef) -> List[RuleNode]:
        """Extrait les règles d'un package"""
        rule_defs = {}
        
        # Trouver les définitions de règles
        for node in ast.walk(package_func):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('rule_'):
                rule_defs[node.name] = node
        
        # Trouver les appels de règles dans l'ordre
        rule_calls = []
        self._extract_rule_execution_order(package_func.body, rule_calls)
        
        # Créer les RuleNodes
        rules = []
        for rule_info in rule_calls:
            if isinstance(rule_info, tuple):
                name, condition = rule_info
            else:
                name = rule_info
                condition = None
            
            rule_def = rule_defs.get(name)
            if rule_def:
                start = rule_def.lineno - 1
                end = rule_def.end_lineno
                rule_code = ''.join(self.source_lines[start:end])
                rule = RuleNode(
                    name=name,
                    code=rule_code,
                    condition=condition,
                    line_start=start,
                    line_end=end
                )
                rules.append(rule)
        
        return rules
    
    def _extract_rule_execution_order(self, body: List[ast.stmt], rule_calls: List):
        """Extrait l'ordre d'exécution des règles avec leurs conditions"""
        for stmt in body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id.startswith('rule_'):
                    rule_calls.append(stmt.value.func.id)
            elif isinstance(stmt, ast.If):
                condition_code = self._ast_to_code(stmt.test)
                for body_stmt in stmt.body:
                    if isinstance(body_stmt, ast.Expr) and isinstance(body_stmt.value, ast.Call):
                        if isinstance(body_stmt.value.func, ast.Name) and body_stmt.value.func.id.startswith('rule_'):
                            rule_calls.append((body_stmt.value.func.id, condition_code))
    
    def _ast_to_code(self, node: ast.AST) -> str:
        """Convertit un node AST en code Python"""
        try:
            return ast.unparse(node)
        except AttributeError:
            # Python < 3.9 fallback
            return self._ast_to_code_fallback(node)
    
    def _ast_to_code_fallback(self, node: ast.AST) -> str:
        """Fallback pour convertir AST en code (Python < 3.9)"""
        if isinstance(node, ast.Compare):
            left = self._ast_to_code_fallback(node.left)
            op = self._ast_to_code_fallback(node.ops[0]) if node.ops else "=="
            right = self._ast_to_code_fallback(node.comparators[0]) if node.comparators else ""
            return f"{left} {op} {right}"
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif hasattr(ast, 'Str') and isinstance(node, ast.Str):
            return repr(node.s)
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return repr(node.n)
        elif isinstance(node, ast.Attribute):
            return f"{self._ast_to_code_fallback(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value = self._ast_to_code_fallback(node.value)
            if hasattr(node, 'slice'):
                if isinstance(node.slice, ast.Index):
                    slice_val = self._ast_to_code_fallback(node.slice.value)
                else:
                    slice_val = self._ast_to_code_fallback(node.slice) if hasattr(node.slice, '__class__') else str(node.slice)
            else:
                slice_val = ""
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Eq):
            return "=="
        elif isinstance(node, ast.NotEq):
            return "!="
        elif isinstance(node, ast.Lt):
            return "<"
        elif isinstance(node, ast.LtE):
            return "<="
        elif isinstance(node, ast.Gt):
            return ">"
        elif isinstance(node, ast.GtE):
            return ">="
        return str(node)


class RuleflowGenerator:
    """Génère le code Python à partir d'une structure RuleflowStructure"""
    
    def __init__(self, structure: RuleflowStructure):
        self.structure = structure
    
    def generate(self) -> str:
        """Génère le code Python complet"""
        lines = []
        
        # Imports
        for imp in self.structure.imports:
            lines.append(imp)
        
        if lines:
            lines.append("")
        
        # Constantes
        for const in self.structure.constants:
            lines.append(const)
        
        if self.structure.constants:
            lines.append("")
        
        # Helper functions
        for helper in self.structure.helper_functions:
            lines.append(helper)
            lines.append("")
        
        # Fonction ruleflow
        lines.append("def ruleflow(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):")
        
        # Générer les packages
        for package in self.structure.packages:
            self._generate_package(lines, package, indent=1)
        
        # Corps de ruleflow - appels des packages
        lines.append("    print(f\"----- Entering ruleflow\")")
        lines.append("")
        
        for package in self.structure.packages:
            if package.condition:
                lines.append(f"    if {package.condition}:")
                lines.append(f"        {package.name}(input, output)")
            else:
                lines.append(f"    {package.name}(input, output)")
        
        lines.append("")
        
        # Classe DecisionEngine
        if self.structure.class_name:
            lines.append(f"class {self.structure.class_name}(CaseHandlingDecisionEngine):")
            lines.append("")
            lines.append("    def _decide(self, input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:")
            lines.append("        # Random value that will be overwritten in the rules")
            lines.append("        output: CaseHandlingDecisionOutput = CaseHandlingDecisionOutput(")
            lines.append("            handling=\"AUTOMATED\",")
            lines.append("            acknowledgement_to_requester=\"N/A\",")
            lines.append("            response_template_id=\"N/A\",")
            lines.append("            work_basket=\"N/A\",")
            lines.append("            priority=\"VERY_LOW\",")
            lines.append("            notes=[],")
            lines.append("            details=[])")
            lines.append("")
            lines.append("        print(f\"----- 🔍 Executing decision engine ruleflow for intention_id='{input.intention_id}'\")")
            lines.append("        ruleflow(input, output)")
            lines.append("")
            lines.append("        return output")
        
        return '\n'.join(lines)
    
    def _generate_package(self, lines: List[str], package: PackageNode, indent: int = 1):
        """Génère le code d'un package"""
        indent_str = "    " * indent
        lines.append(f"{indent_str}def {package.name}(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):")
        
        # Générer les règles
        for rule in package.rules:
            self._generate_rule(lines, rule, indent + 1)
        
        # Appels des règles
        lines.append(f"{indent_str}    print(f\"------- 📦 Executing {package.name}\")")
        lines.append("")
        
        for rule in package.rules:
            if rule.condition:
                lines.append(f"{indent_str}    if {rule.condition}:")
                lines.append(f"{indent_str}        {rule.name}(input, output)")
            else:
                lines.append(f"{indent_str}    {rule.name}(input, output)")
        
        lines.append("")
        lines.append("")
    
    def _generate_rule(self, lines: List[str], rule: RuleNode, indent: int = 1):
        """Génère le code d'une règle"""
        indent_str = "    " * indent
        # Utiliser le code original de la règle avec l'indentation correcte
        rule_lines = rule.code.split('\n')
        for line in rule_lines:
            # Si la ligne est vide, on la garde telle quelle
            if line.strip() == '':
                lines.append('')
            else:
                # Retirer l'indentation existante et ajouter la nouvelle
                stripped = line.lstrip()
                if stripped:
                    lines.append(f"{indent_str}{stripped}")
                else:
                    lines.append('')
        # Ajouter une ligne vide après la règle
        lines.append("")



