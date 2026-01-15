from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

_LOGGER = logging.getLogger(__name__)


class NodeType(str, Enum):
    PACKAGE = "package"
    RULE = "rule"
    CONDITION = "condition"


@dataclass
class OutputAssignment:
    """Représente une affectation à l'objet output."""

    attribute: str  # ex: "priority", "work_basket", "acknowledgement_to_requester"
    value: Any  # ex: "HIGH", work_basket_accueil, f"#VISIT_PAGE,{text},{url}"
    line_number: int = 0


@dataclass
class RuleNode:
    """Représente une règle dans le ruleflow."""

    name: str
    code: str
    free_code: str = ""  # Code libre (logique métier, calculs, conditions)
    output_assignments: list[OutputAssignment] = field(
        default_factory=list,
    )  # Paramètres output structurés
    condition: str | None = None
    line_start: int = 0
    line_end: int = 0


@dataclass
class PackageNode:
    """Représente un package dans le ruleflow."""

    name: str
    rules: list[RuleNode] = field(default_factory=list)
    condition: str | None = None
    line_start: int = 0
    line_end: int = 0
    execution_order: int = 0


@dataclass
class RuleflowStructure:
    """Structure complète du ruleflow."""

    imports: list[str] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)
    helper_functions: list[str] = field(default_factory=list)
    packages: list[PackageNode] = field(default_factory=list)
    class_name: str = ""
    ruleflow_function_start: int = 0
    ruleflow_function_end: int = 0
    class_start: int = 0
    class_end: int = 0


class RuleflowParser:
    """Parse un fichier decision_engine.py pour extraire la structure du ruleflow."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.source_lines: list[str] = []
        self.ast_tree: ast.AST | None = None

    def parse(self) -> RuleflowStructure:
        """Parse le fichier et retourne la structure."""
        with open(self.file_path, encoding="utf-8") as f:
            self.source_lines = f.readlines()

        source_code = "".join(self.source_lines)
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

    def _extract_imports(self) -> list[str]:
        """Extrait les imports."""
        imports = []
        seen = set()
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line_num = node.lineno - 1
                if line_num < len(self.source_lines) and line_num not in seen:
                    imports.append(self.source_lines[line_num].strip())
                    seen.add(line_num)
        return sorted(set(imports))

    def _extract_constants(self) -> list[str]:
        """Extrait les constantes (variables en majuscules)."""
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

    def _extract_helper_functions(self) -> list[str]:
        """Extrait les fonctions helper (hors ruleflow, packages, règles et classe)."""
        helpers = []
        ruleflow_names = {"ruleflow", "visualize_ruleflow"}
        ruleflow_func = self._find_ruleflow_function()

        # Collecter tous les noms de packages et règles pour les exclure
        excluded_names = set()
        if ruleflow_func:
            for node in ast.walk(ruleflow_func):
                if isinstance(node, ast.FunctionDef):
                    excluded_names.add(node.name)

        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                # Exclure ruleflow, packages, règles, et fonctions dans les classes
                if (
                    node.name not in ruleflow_names
                    and not self._is_in_class(node)
                    and node.name not in excluded_names
                    and not node.name.startswith("package_")
                    and not node.name.startswith("rule_")
                ):
                    start = node.lineno - 1
                    end = node.end_lineno
                    func_code = "".join(self.source_lines[start:end])
                    helpers.append(func_code)

        return helpers

    def _is_in_class(self, node: ast.AST) -> bool:
        """Vérifie si un node est dans une classe."""
        # Parcourir l'AST pour trouver la classe parente
        class_nodes = [
            n for n in ast.walk(self.ast_tree) if isinstance(n, ast.ClassDef)
        ]
        for class_node in class_nodes:
            for child in ast.walk(class_node):
                if child == node:
                    return True
        return False

    def _find_ruleflow_function(self) -> ast.FunctionDef | None:
        """Trouve la fonction ruleflow."""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == "ruleflow":
                # Vérifier qu'elle n'est pas dans une classe
                if not self._is_in_class(node):
                    return node
        return None

    def _find_decision_engine_class(self) -> ast.ClassDef | None:
        """Trouve la classe DecisionEngine."""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                # Chercher une classe qui hérite de CaseHandlingDecisionEngine
                for base in node.bases:
                    if isinstance(base, ast.Name) and "DecisionEngine" in base.id:
                        return node
                    elif isinstance(base, ast.Attribute):
                        if "DecisionEngine" in base.attr:
                            return node
        # Si pas trouvé par l'héritage, chercher par nom de classe
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                if "DecisionEngine" in node.name:
                    return node
        return None

    def _extract_packages(self, ruleflow_func: ast.FunctionDef) -> list[PackageNode]:
        """Extrait les packages de la fonction ruleflow."""
        package_defs = {}

        # Trouver les définitions de packages
        for node in ast.walk(ruleflow_func):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("package_"):
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
                    line_end=pkg_def.end_lineno,
                )
                package.rules = self._extract_rules_from_package(pkg_def)
                packages.append(package)

        return packages

    def _extract_package_execution_order(
        self,
        body: list[ast.stmt],
        execution_order: list[tuple],
    ) -> None:
        """Extrait l'ordre d'exécution des packages avec leurs conditions."""
        for stmt in body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(
                    stmt.value.func,
                    ast.Name,
                ) and stmt.value.func.id.startswith("package_"):
                    execution_order.append((stmt.value.func.id, None))
            elif isinstance(stmt, ast.If):
                # Extraire la condition
                condition_code = self._ast_to_code(stmt.test)
                for body_stmt in stmt.body:
                    if isinstance(body_stmt, ast.Expr) and isinstance(
                        body_stmt.value,
                        ast.Call,
                    ):
                        if isinstance(
                            body_stmt.value.func,
                            ast.Name,
                        ) and body_stmt.value.func.id.startswith("package_"):
                            execution_order.append(
                                (body_stmt.value.func.id, condition_code),
                            )
                    elif isinstance(body_stmt, ast.If):
                        self._extract_package_execution_order(
                            [body_stmt],
                            execution_order,
                        )

    def _extract_rules_from_package(
        self,
        package_func: ast.FunctionDef,
    ) -> list[RuleNode]:
        """Extrait les règles d'un package."""
        rule_defs = {}

        # Trouver les définitions de règles
        for node in ast.walk(package_func):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("rule_"):
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
                rule_code = "".join(self.source_lines[start:end])
                # Analyser le code de la règle pour séparer code libre et paramètres output
                free_code, output_assignments = self._analyze_rule_code(
                    rule_def,
                    rule_code,
                )

                rule = RuleNode(
                    name=name,
                    code=rule_code,
                    free_code=free_code,
                    output_assignments=output_assignments,
                    condition=condition,
                    line_start=start,
                    line_end=end,
                )
                rules.append(rule)

        return rules

    def _extract_rule_execution_order(
        self, body: list[ast.stmt], rule_calls: list
    ) -> None:
        """Extrait l'ordre d'exécution des règles avec leurs conditions."""
        for stmt in body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(
                    stmt.value.func,
                    ast.Name,
                ) and stmt.value.func.id.startswith("rule_"):
                    rule_calls.append(stmt.value.func.id)
            elif isinstance(stmt, ast.If):
                condition_code = self._ast_to_code(stmt.test)
                for body_stmt in stmt.body:
                    if isinstance(body_stmt, ast.Expr) and isinstance(
                        body_stmt.value,
                        ast.Call,
                    ):
                        if isinstance(
                            body_stmt.value.func,
                            ast.Name,
                        ) and body_stmt.value.func.id.startswith("rule_"):
                            rule_calls.append((body_stmt.value.func.id, condition_code))

    def _ast_to_code(self, node: ast.AST) -> str:
        """Convertit un node AST en code Python."""
        try:
            return ast.unparse(node)
        except AttributeError:
            # Python < 3.9 fallback
            return self._ast_to_code_fallback(node)

    def _ast_to_code_fallback(self, node: ast.AST) -> str:
        """Fallback pour convertir AST en code (Python < 3.9)."""
        if isinstance(node, ast.Compare):
            left = self._ast_to_code_fallback(node.left)
            op = self._ast_to_code_fallback(node.ops[0]) if node.ops else "=="
            right = (
                self._ast_to_code_fallback(node.comparators[0])
                if node.comparators
                else ""
            )
            return f"{left} {op} {right}"
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif hasattr(ast, "Str") and isinstance(node, ast.Str):
            return repr(node.s)
        elif hasattr(ast, "Num") and isinstance(node, ast.Num):
            return repr(node.n)
        elif isinstance(node, ast.Attribute):
            return f"{self._ast_to_code_fallback(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value = self._ast_to_code_fallback(node.value)
            if hasattr(node, "slice"):
                if isinstance(node.slice, ast.Index):
                    slice_val = self._ast_to_code_fallback(node.slice.value)
                else:
                    slice_val = (
                        self._ast_to_code_fallback(node.slice)
                        if hasattr(node.slice, "__class__")
                        else str(node.slice)
                    )
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

    def _analyze_rule_code(
        self,
        rule_func: ast.FunctionDef,
        rule_code: str,
    ) -> tuple[str, list[OutputAssignment]]:
        """Analyse le code d'une règle pour séparer le code libre des affectations à output.

        Args:
        ----
            rule_func: AST de la fonction de règle
            rule_code: Code source complet de la règle

        Returns:
        -------
            Tuple contenant (code_libre, liste_des_affectations_output)

        """
        output_assignments = []

        # Analyser tous les statements de la règle de manière récursive
        self._extract_output_assignments_recursive(
            rule_func.body,
            output_assignments,
            rule_func.lineno,
        )

        # Pour le code libre, on garde le code original en enlevant seulement
        # les lignes qui sont des affectations directes à output
        free_code = self._generate_free_code(rule_code, output_assignments)

        return free_code, output_assignments

    def _extract_output_assignments_recursive(
        self,
        stmts: list[ast.stmt],
        assignments: list[OutputAssignment],
        base_line: int,
    ) -> None:
        """Extrait récursivement toutes les affectations à output, même dans des conditions imbriquées."""
        for stmt in stmts:
            if isinstance(stmt, ast.Assign):
                # Vérifier si c'est une affectation à output
                for target in stmt.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "output"
                    ):
                        try:
                            value_code = self._ast_to_code(stmt.value)
                            assignment = OutputAssignment(
                                attribute=target.attr,
                                value=value_code,
                                line_number=stmt.lineno - base_line,
                            )
                            assignments.append(assignment)
                        except Exception as exc:
                            _LOGGER.debug(
                                "Skipping output assignment at line %s: %s",
                                stmt.lineno,
                                exc,
                            )

            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Vérifier si c'est un appel de méthode sur output
                call = stmt.value
                if (
                    isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Attribute)
                    and isinstance(call.func.value.value, ast.Name)
                    and call.func.value.value.id == "output"
                    and call.func.attr == "append"
                ):
                    try:
                        # output.details.append() ou output.notes.append()
                        list_attr = call.func.value.attr
                        if call.args:
                            value_code = self._ast_to_code(call.args[0])
                            assignment = OutputAssignment(
                                attribute=f"{list_attr}.append",
                                value=value_code,
                                line_number=stmt.lineno - base_line,
                            )
                            assignments.append(assignment)
                    except Exception as exc:
                        _LOGGER.debug(
                            "Skipping output append at line %s: %s",
                            stmt.lineno,
                            exc,
                        )

            elif isinstance(stmt, ast.If):
                # Analyser récursivement le corps de la condition if
                self._extract_output_assignments_recursive(
                    stmt.body,
                    assignments,
                    base_line,
                )
                # Analyser récursivement la partie else
                self._extract_output_assignments_recursive(
                    stmt.orelse,
                    assignments,
                    base_line,
                )

            elif isinstance(stmt, ast.For):
                # Analyser récursivement le corps de la boucle for
                self._extract_output_assignments_recursive(
                    stmt.body,
                    assignments,
                    base_line,
                )
                self._extract_output_assignments_recursive(
                    stmt.orelse,
                    assignments,
                    base_line,
                )

            elif isinstance(stmt, ast.While):
                # Analyser récursivement le corps de la boucle while
                self._extract_output_assignments_recursive(
                    stmt.body,
                    assignments,
                    base_line,
                )
                self._extract_output_assignments_recursive(
                    stmt.orelse,
                    assignments,
                    base_line,
                )

            elif isinstance(stmt, ast.Try):
                # Analyser récursivement les blocs try/except/finally
                self._extract_output_assignments_recursive(
                    stmt.body,
                    assignments,
                    base_line,
                )
                for handler in stmt.handlers:
                    self._extract_output_assignments_recursive(
                        handler.body,
                        assignments,
                        base_line,
                    )
                self._extract_output_assignments_recursive(
                    stmt.orelse,
                    assignments,
                    base_line,
                )
                self._extract_output_assignments_recursive(
                    stmt.finalbody,
                    assignments,
                    base_line,
                )

    def _generate_free_code(
        self,
        rule_code: str,
        output_assignments: list[OutputAssignment],
    ) -> str:
        """Génère le code libre en gardant tout le code sauf les lignes d'affectation output simples.
        Pour l'instant, on garde tout le code original car c'est plus sûr.
        """
        # Extraction des lignes qui ne sont que du code libre (sans affectations output simples)
        lines = rule_code.split("\n")

        # Garder la signature de fonction et tout le code pour l'instant
        # Plus tard on pourra être plus fin dans l'extraction
        free_lines = []

        for i, line in enumerate(lines):
            # Ignorer la signature de fonction
            if i == 0:
                continue

            # Pour l'instant, garder toutes les lignes qui ne sont pas des affectations simples
            stripped_line = line.strip()

            # Ignorer les lignes d'affectation directe à output (hors conditions)
            if (
                stripped_line.startswith("output.")
                and "=" in stripped_line
                and not stripped_line.startswith("if ")
                and not stripped_line.startswith("elif ")
                and not line.strip().startswith("# ")
            ):
                continue

            # Ignorer les appels directs à output.X.append (hors conditions)
            if (
                stripped_line.startswith("output.")
                and ".append(" in stripped_line
                and not stripped_line.startswith("if ")
                and not stripped_line.startswith("elif ")
            ):
                continue

            free_lines.append(line)

        return "\n".join(free_lines)


class RuleflowGenerator:
    """Génère le code Python à partir d'une structure RuleflowStructure."""

    def __init__(self, structure: RuleflowStructure) -> None:
        self.structure = structure

    def generate(self) -> str:
        """Génère le code Python complet."""
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
        lines.append(
            "def ruleflow(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):",
        )

        # Générer les packages DANS la fonction ruleflow
        for package in self.structure.packages:
            self._generate_package(lines, package, indent=1)

        # Corps de ruleflow - appels des packages
        lines.append('    print(f"----- Entering ruleflow")')

        for package in self.structure.packages:
            if package.condition:
                lines.append(f"    if {package.condition}:")
                lines.append(f"        {package.name}(input, output)")
            else:
                lines.append(f"    {package.name}(input, output)")

        lines.append("")

        # Classe DecisionEngine
        if self.structure.class_name:
            lines.append(
                f"class {self.structure.class_name}(CaseHandlingDecisionEngine):",
            )
            lines.append("")
            lines.append(
                "    def _decide(self, input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:",
            )
            lines.append("        # Random value that will be overwritten in the rules")
            lines.append(
                "        output: CaseHandlingDecisionOutput = CaseHandlingDecisionOutput(",
            )
            lines.append('            handling="AUTOMATED",')
            lines.append('            acknowledgement_to_requester="N/A",')
            lines.append('            response_template_id="N/A",')
            lines.append('            work_basket="N/A",')
            lines.append('            priority="VERY_LOW",')
            lines.append("            notes=[],")
            lines.append("            details=[])")
            lines.append("")
            lines.append(
                "        print(f\"----- 🔍 Executing decision engine ruleflow for intention_id='{input.intention_id}'\")",
            )
            lines.append("        ruleflow(input, output)")
            lines.append("")
            lines.append("        return output")

        return "\n".join(lines)

    def _generate_package(
        self,
        lines: list[str],
        package: PackageNode,
        indent: int = 1,
    ) -> None:
        """Génère le code d'un package."""
        indent_str = "    " * indent
        lines.append(
            f"{indent_str}def {package.name}(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):",
        )

        # Générer les règles
        for rule in package.rules:
            self._generate_rule(lines, rule, indent + 1)

        # Appels des règles
        lines.append(f'{indent_str}    print(f"------- 📦 Executing {package.name}")')
        lines.append("")

        for rule in package.rules:
            if rule.condition:
                lines.append(f"{indent_str}    if {rule.condition}:")
                lines.append(f"{indent_str}        {rule.name}(input, output)")
            else:
                lines.append(f"{indent_str}    {rule.name}(input, output)")

        lines.append("")
        lines.append("")

    def _generate_rule(self, lines: list[str], rule: RuleNode, indent: int = 1) -> None:
        """Génère le code d'une règle."""
        indent_str = "    " * indent

        # Vérifier si la règle a le code libre et les paramètres séparés
        if (
            hasattr(rule, "free_code")
            and hasattr(rule, "output_assignments")
            and rule.free_code
        ):
            # Générer à partir du code libre et des paramètres séparés
            self._generate_rule_from_components(lines, rule, indent_str)
        else:
            # Mode de compatibilité : utiliser le code complet
            self._generate_rule_from_full_code(lines, rule, indent_str)

        # Ajouter une ligne vide après la règle
        lines.append("")

    def _generate_rule_from_full_code(
        self,
        lines: list[str],
        rule: RuleNode,
        indent_str: str,
    ) -> None:
        """Génère une règle à partir du code complet (mode compatibilité)."""
        rule_lines = rule.code.rstrip().split("\n")

        # Trouver l'indentation minimale de TOUTES les lignes (y compris la première)
        non_empty_lines = [line for line in rule_lines if line.strip()]
        if non_empty_lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        else:
            min_indent = 0

        # Traiter chaque ligne
        for line in rule_lines:
            if line.strip() == "":
                lines.append("")
            else:
                # Retirer TOUTE l'indentation originale et ajouter la nouvelle
                stripped = (
                    line[min_indent:] if len(line) >= min_indent else line.lstrip()
                )
                lines.append(f"{indent_str}{stripped}")

    def _generate_rule_from_components(
        self,
        lines: list[str],
        rule: RuleNode,
        indent_str: str,
    ) -> None:
        """Génère une règle à partir du code libre et des paramètres output séparés."""
        # Extraire la signature de la fonction depuis le code complet
        rule_lines = rule.code.split("\n")
        function_signature = ""

        for line in rule_lines:
            if line.strip().startswith("def "):
                function_signature = line.strip()
                break

        if not function_signature:
            function_signature = f"def {rule.name}(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):"

        # Ajouter la signature de la fonction
        lines.append(f"{indent_str}{function_signature}")

        # Ajouter le code libre si présent
        if rule.free_code and rule.free_code.strip():
            free_code_lines = rule.free_code.split("\n")
            for line in free_code_lines:
                if line.strip():
                    lines.append(f"{indent_str}    {line}")
                else:
                    lines.append("")

        # Ajouter les affectations output
        if hasattr(rule, "output_assignments") and rule.output_assignments:
            lines.append(f"{indent_str}    # Mise à jour des paramètres output")
            for assignment in rule.output_assignments:
                if assignment.attribute.endswith(".append"):
                    # Gestion des appels de méthode comme output.details.append()
                    attr_base = assignment.attribute.replace(".append", "")
                    lines.append(
                        f"{indent_str}    output.{attr_base}.append({assignment.value})",
                    )
                else:
                    # Affectation directe
                    lines.append(
                        f"{indent_str}    output.{assignment.attribute} = {assignment.value}",
                    )
