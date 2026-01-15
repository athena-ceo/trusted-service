import os
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

try:
    from .ruleflow_config_models import GenerateFromConfigRequest
    from .ruleflow_parser import (
        PackageNode,
        RuleflowGenerator,
        RuleflowParser,
        RuleNode,
    )
except ImportError:
    # Fallback for direct import
    from src.backend.ruleflow.ruleflow_config_models import GenerateFromConfigRequest
    from src.backend.ruleflow.ruleflow_parser import (
        PackageNode,
        RuleflowGenerator,
        RuleflowParser,
        RuleNode,
    )

router = APIRouter(prefix="/api/v1/ruleflow", tags=["Ruleflow Editor"])


# Modèles Pydantic pour les requêtes/réponses
class PackageDict(BaseModel):
    name: str
    condition: Optional[str] = None
    execution_order: int
    rules: List[dict]


class RuleflowStructureResponse(BaseModel):
    imports: List[str]
    constants: List[str]
    helper_functions: List[str]
    packages: List[dict]
    class_name: str


class PackageUpdateRequest(BaseModel):
    name: str
    condition: Optional[str] = None
    execution_order: int


class RuleUpdateRequest(BaseModel):
    package_name: str
    rule_name: str
    code: str
    condition: Optional[str] = None


class CreateAppRequest(BaseModel):
    runtime_dir: str
    app_name: str
    class_name: str = "DecisionEngine"


class MoveItemRequest(BaseModel):
    direction: str  # "up" or "down"


class AddRuleRequest(BaseModel):
    package_name: str
    rule_name: str
    rule_code: str
    condition: Optional[str] = None


class UpdatePackageConditionRequest(BaseModel):
    package_name: str
    condition: Optional[str] = None


# Variable globale pour stocker le répertoire de base - à configurer selon votre environnement
def get_base_runtime_dir() -> Path:
    """Retourne le répertoire de base des runtime."""
    # Essayer de récupérer depuis une variable d'environnement
    base = os.getenv(
        "TRUSTED_SERVICES_BASE_DIR",
        "/Users/joel/Documents/Dev/Athena/trusted-service",
    )
    return Path(base)


@router.get("/runtime-directories")
async def get_runtime_directories() -> List[str]:
    """Liste tous les répertoires runtime disponibles."""
    base_path = get_base_runtime_dir()
    runtime_dirs = []

    # Chercher les répertoires qui contiennent un dossier apps
    if base_path.exists():
        for item in base_path.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and (item / "apps").exists()
            ):
                runtime_dirs.append(item.name)

    return sorted(runtime_dirs)


@router.get("/runtime/{runtime_dir}/apps")
async def get_apps(runtime_dir: str) -> List[str]:
    """Liste toutes les apps dans un runtime."""
    apps_path = get_base_runtime_dir() / runtime_dir / "apps"
    if not apps_path.exists():
        raise HTTPException(status_code=404, detail="Runtime directory not found")

    apps = [
        d.name for d in apps_path.iterdir() if d.is_dir() and not d.name.startswith(".")
    ]
    return sorted(apps)


@router.get("/runtime/{runtime_dir}/apps/{app_name}/structure")
async def get_ruleflow_structure(
    runtime_dir: str,
    app_name: str,
) -> RuleflowStructureResponse:
    """Récupère la structure du ruleflow d'une app."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    try:
        parser = RuleflowParser(decision_engine_path)
        structure = parser.parse()
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        # Lire le fichier pour afficher le contexte
        try:
            with open(decision_engine_path, encoding="utf-8") as f:
                lines = f.readlines()
                if syntax_err.lineno and syntax_err.lineno <= len(lines):
                    pass
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Syntax error in decision_engine.py at line {syntax_err.lineno}: {syntax_err!s}",
        )
    except Exception as e:
        import traceback

        traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Error parsing ruleflow: {e!s}")

    # Convertir les packages en dict pour la sérialisation JSON
    packages_dict = []
    for pkg in structure.packages:
        pkg_dict = {
            "name": pkg.name,
            "condition": pkg.condition,
            "execution_order": pkg.execution_order,
            "rules": [
                {
                    "name": rule.name,
                    "code": rule.code,
                    "condition": rule.condition,
                    "free_code": getattr(rule, "free_code", None),
                    "output_assignments": [
                        {
                            "parameter": assignment.attribute,
                            "value": assignment.value,
                            "line_number": assignment.line_number,
                        }
                        for assignment in (
                            getattr(rule, "output_assignments", None) or []
                        )
                    ],
                }
                for rule in pkg.rules
            ],
        }
        packages_dict.append(pkg_dict)

    return RuleflowStructureResponse(
        imports=structure.imports,
        constants=structure.constants,
        helper_functions=structure.helper_functions,
        packages=packages_dict,
        class_name=structure.class_name,
    )


@router.get("/runtime/{runtime_dir}/apps/{app_name}/config")
async def get_ruleflow_config(runtime_dir: str, app_name: str):
    """Convertit decision_engine.py en format JSON de configuration pour l'éditeur."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    try:
        parser = RuleflowParser(decision_engine_path)
        structure = parser.parse()

        # Générer des IDs uniques pour les packages et règles
        import uuid

        # Convertir en format RuleflowConfig
        packages_config = []
        for pkg in structure.packages:
            rules_config = []
            for rule in pkg.rules:
                rules_config.append(
                    {
                        "id": str(uuid.uuid4()),
                        "name": rule.name,
                        "code": rule.code,
                        "condition": rule.condition,
                    },
                )

            packages_config.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": pkg.name,
                    "condition": pkg.condition,
                    "execution_order": pkg.execution_order,
                    "rules": rules_config,
                },
            )

        # Créer la configuration complète
        from datetime import datetime

        config = {
            "version": "1.0",
            "metadata": {
                "app_name": app_name,
                "class_name": structure.class_name or "DecisionEngine",
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "runtime": runtime_dir,
            },
            "imports": structure.imports,
            "constants": structure.constants,
            "helper_functions": structure.helper_functions,
            "packages": packages_config,
        }

        return {"config": config}
    except Exception as e:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error converting decision_engine.py to config: {e!s}",
        )


@router.post("/runtime/{runtime_dir}/apps/{app_name}/package/move")
async def move_package(
    runtime_dir: str,
    app_name: str,
    package_name: str,
    request: MoveItemRequest = Body(...),
):
    """Déplace un package vers le haut ou le bas."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Trouver le package à déplacer
    package_index = next(
        (i for i, pkg in enumerate(structure.packages) if pkg.name == package_name),
        None,
    )
    if package_index is None:
        raise HTTPException(status_code=404, detail="Package not found")

    # Déplacer
    if request.direction == "up" and package_index > 0:
        structure.packages[package_index], structure.packages[package_index - 1] = (
            structure.packages[package_index - 1],
            structure.packages[package_index],
        )
        # Mettre à jour les execution_order
        for i, pkg in enumerate(structure.packages):
            pkg.execution_order = i
    elif request.direction == "down" and package_index < len(structure.packages) - 1:
        structure.packages[package_index], structure.packages[package_index + 1] = (
            structure.packages[package_index + 1],
            structure.packages[package_index],
        )
        # Mettre à jour les execution_order
        for i, pkg in enumerate(structure.packages):
            pkg.execution_order = i

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Package {package_name} moved {request.direction}"}


@router.post("/runtime/{runtime_dir}/apps/{app_name}/package/add")
async def add_package(
    runtime_dir: str,
    app_name: str,
    package: PackageUpdateRequest = Body(...),
):
    """Ajoute un nouveau package."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    try:
        parser = RuleflowParser(decision_engine_path)
        structure = parser.parse()

        # Vérifier que le package n'existe pas déjà
        if any(pkg.name == package.name for pkg in structure.packages):
            raise HTTPException(status_code=400, detail="Package already exists")

        # Créer le nouveau package avec une règle par défaut
        # Le code de la règle doit être sans indentation (le générateur l'ajoutera)
        default_rule_code = """def rule_default(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
    output.details.append("rule_default")
    output.acknowledgement_to_requester = "#ACK"
    output.response_template_id = ""
    output.work_basket = "default"
    output.priority = "MEDIUM"
    output.handling = "DEFLECTION"
"""
        new_package = PackageNode(
            name=package.name,
            condition=package.condition,
            execution_order=package.execution_order,
            rules=[RuleNode(name="rule_default", code=default_rule_code)],
        )

        # Insérer le package à la bonne position
        structure.packages.insert(package.execution_order, new_package)
        # Mettre à jour les execution_order
        for i, pkg in enumerate(structure.packages):
            pkg.execution_order = i

        # Régénérer le fichier
        generator = RuleflowGenerator(structure)
        new_code = generator.generate()

        # Valider que le code généré est syntaxiquement correct
        try:
            import ast

            ast.parse(new_code)
        except SyntaxError as syntax_err:
            import traceback

            traceback.format_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Generated code has syntax error: {syntax_err!s}",
            )

        # Sauvegarder le fichier
        with open(decision_engine_path, "w", encoding="utf-8") as f:
            f.write(new_code)

        return {"message": f"Package {package.name} added"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback

        traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Error adding package: {e!s}")


@router.delete("/runtime/{runtime_dir}/apps/{app_name}/package/{package_name}")
async def delete_package(runtime_dir: str, app_name: str, package_name: str):
    """Supprime un package."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Supprimer le package
    structure.packages = [pkg for pkg in structure.packages if pkg.name != package_name]

    # Mettre à jour les execution_order
    for i, pkg in enumerate(structure.packages):
        pkg.execution_order = i

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Package {package_name} deleted"}


@router.post("/runtime/{runtime_dir}/apps/{app_name}/package/condition")
async def update_package_condition(
    runtime_dir: str,
    app_name: str,
    request: UpdatePackageConditionRequest = Body(...),
):
    """Met à jour la condition d'un package."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Trouver et mettre à jour le package
    package = next(
        (pkg for pkg in structure.packages if pkg.name == request.package_name),
        None,
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    package.condition = request.condition

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Package {request.package_name} condition updated"}


@router.post("/runtime/{runtime_dir}/apps/{app_name}/rule/move")
async def move_rule(
    runtime_dir: str,
    app_name: str,
    package_name: str,
    rule_name: str,
    request: MoveItemRequest = Body(...),
):
    """Déplace une règle dans un package."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Trouver le package
    package = next(
        (pkg for pkg in structure.packages if pkg.name == package_name),
        None,
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Trouver la règle
    rule_index = next(
        (i for i, rule in enumerate(package.rules) if rule.name == rule_name),
        None,
    )
    if rule_index is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Déplacer
    if request.direction == "up" and rule_index > 0:
        package.rules[rule_index], package.rules[rule_index - 1] = (
            package.rules[rule_index - 1],
            package.rules[rule_index],
        )
    elif request.direction == "down" and rule_index < len(package.rules) - 1:
        package.rules[rule_index], package.rules[rule_index + 1] = (
            package.rules[rule_index + 1],
            package.rules[rule_index],
        )

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Rule {rule_name} moved {request.direction}"}


@router.post("/runtime/{runtime_dir}/apps/{app_name}/rule/update")
async def update_rule(
    runtime_dir: str,
    app_name: str,
    rule: RuleUpdateRequest = Body(...),
):
    """Met à jour une règle."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Trouver le package
    package = next(
        (pkg for pkg in structure.packages if pkg.name == rule.package_name),
        None,
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Trouver et mettre à jour la règle
    rule_node = next((r for r in package.rules if r.name == rule.rule_name), None)
    if not rule_node:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule_node.code = rule.code
    rule_node.condition = rule.condition

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Rule {rule.rule_name} updated"}


@router.post("/runtime/{runtime_dir}/apps/{app_name}/rule/add")
async def add_rule(
    runtime_dir: str,
    app_name: str,
    request: AddRuleRequest = Body(...),
):
    """Ajoute une nouvelle règle."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Trouver le package
    package = next(
        (pkg for pkg in structure.packages if pkg.name == request.package_name),
        None,
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Vérifier que la règle n'existe pas déjà
    if any(rule.name == request.rule_name for rule in package.rules):
        raise HTTPException(status_code=400, detail="Rule already exists")

    # Ajouter la nouvelle règle
    new_rule = RuleNode(
        name=request.rule_name,
        code=request.rule_code,
        condition=request.condition,
    )
    package.rules.append(new_rule)

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Rule {request.rule_name} added"}


@router.delete("/runtime/{runtime_dir}/apps/{app_name}/rule/{package_name}/{rule_name}")
async def delete_rule(
    runtime_dir: str,
    app_name: str,
    package_name: str,
    rule_name: str,
):
    """Supprime une règle."""
    decision_engine_path = (
        get_base_runtime_dir() / runtime_dir / "apps" / app_name / "decision_engine.py"
    )

    if not decision_engine_path.exists():
        raise HTTPException(status_code=404, detail="decision_engine.py not found")

    parser = RuleflowParser(decision_engine_path)
    structure = parser.parse()

    # Trouver le package
    package = next(
        (pkg for pkg in structure.packages if pkg.name == package_name),
        None,
    )
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Supprimer la règle
    package.rules = [rule for rule in package.rules if rule.name != rule_name]

    # Régénérer le fichier
    generator = RuleflowGenerator(structure)
    new_code = generator.generate()

    # Valider que le code généré est syntaxiquement correct
    try:
        import ast

        ast.parse(new_code)
    except SyntaxError as syntax_err:
        import traceback

        traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Generated code has syntax error: {syntax_err!s}",
        )

    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    return {"message": f"Rule {rule_name} deleted"}


@router.post("/runtime/create")
async def create_runtime_directory(runtime_name: str):
    """Crée un nouveau répertoire runtime."""
    runtime_path = get_base_runtime_dir() / runtime_name
    if runtime_path.exists():
        raise HTTPException(status_code=400, detail="Runtime directory already exists")

    runtime_path.mkdir(parents=True)
    (runtime_path / "apps").mkdir()
    (runtime_path / "cache").mkdir()

    return {"message": f"Runtime directory {runtime_name} created"}


@router.post("/runtime/{runtime_dir}/apps/create")
async def create_app(runtime_dir: str, request: CreateAppRequest = Body(...)):
    """Crée une nouvelle app avec un decision_engine.py de base."""
    apps_path = get_base_runtime_dir() / runtime_dir / "apps"
    if not apps_path.exists():
        raise HTTPException(status_code=404, detail="Runtime directory not found")

    app_path = apps_path / request.app_name
    if app_path.exists():
        raise HTTPException(status_code=400, detail="App already exists")

    app_path.mkdir()

    # Créer un fichier decision_engine.py de base
    template = f"""from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput


def ruleflow(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
    def package_initialisations(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_decision_par_defaut(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            output.details.append("rule_decision_par_defaut")
            output.acknowledgement_to_requester = "#ACK"
            output.response_template_id = ""
            output.work_basket = "default"
            output.priority = "MEDIUM"
            output.handling = "DEFLECTION"

        print(f"------- 📦 Executing package_initialisations")
        rule_decision_par_defaut(input, output)

    print(f"----- Entering ruleflow")
    package_initialisations(input, output)


class {request.class_name}(CaseHandlingDecisionEngine):
    def _decide(self, input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        output: CaseHandlingDecisionOutput = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="N/A",
            response_template_id="N/A",
            work_basket="N/A",
            priority="VERY_LOW",
            notes=[],
            details=[])

        print(f"----- 🔍 Executing {request.app_name} decision engine ruleflow for intention_id='{{input.intention_id}}'")
        ruleflow(input, output)

        return output
"""

    decision_engine_path = app_path / "decision_engine.py"
    with open(decision_engine_path, "w", encoding="utf-8") as f:
        f.write(template)

    return {"message": f"App {request.app_name} created"}


# Nouvel endpoint pour la génération depuis le format pivot
@router.post("/generate-from-config")
async def generate_from_config(request: GenerateFromConfigRequest):
    """Génère le code Python à partir d'une configuration ruleflow JSON."""
    try:
        from .ruleflow_config_models import RuleflowConfigGenerator

        generator = RuleflowConfigGenerator()

        # Valider la configuration
        errors = generator.validate_config(request.config)
        if errors:
            raise HTTPException(status_code=400, detail={"validation_errors": errors})

        # Déterminer le chemin du fichier
        runtime_path = Path("../") / request.config.metadata.runtime
        app_path = runtime_path / "apps" / request.config.metadata.app_name
        file_path = app_path / "decision_engine.py"

        # Générer et sauvegarder le code
        generated_code = generator.save_to_file(request.config, str(file_path))

        return {
            "message": f"Code généré pour {request.config.metadata.app_name}",
            "generated_code": generated_code,
            "file_path": str(file_path),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération: {e!s}",
        )
