from datetime import datetime
from typing import Literal

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput

work_basket_accueil = "accueil"
work_basket_pref_etrangers_aes_salarie = "pref-etrangers-aes-salarie"
work_basket_api_a_renouveler = "api-a-renouveler"
work_basket_asile_priorite = "asile-priorite"
work_basket_atda = "atda"
work_basket_generique = "generique"
work_basket_dublin = "dublin"
work_basket_reorientation = "reorientation"
work_basket_sauf_conduits = "sauf-conduits"
work_basket_ukraine = "ukraine"
work_basket_autres = "autres"

response_template_id_api_a_renouveler = "api-a-renouveler"
response_template_id_atda = "atda"
response_template_id_dublin = "dublin"
response_template_id_sauf_conduits = "sauf-conduits"


def days_between(date_begin: str, date_end: str) -> int:
    """
    Returns the number of days between two dates in 'd/M/yyyy' format.
    The result is positive if date_end is after date_begin, negative otherwise.
    """
    fmt = "%d/%m/%Y"
    d1 = datetime.strptime(date_begin, fmt)
    d2 = datetime.strptime(date_end, fmt)
    return (d2 - d1).days


def jours_jusqu_a_date(input: CaseHandlingDecisionInput, date: str) -> int:
    date_demande = input.field_values["date_demande"]
    date_fin = input.field_values[date]
    return days_between(date_begin=date_demande, date_end=date_fin)


def augmenter_niveau_priorite(output: CaseHandlingDecisionOutput):
    priorities: list[Literal["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]] = ["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    try:
        index = priorities.index(output.priority)
        if index + 1 < len(priorities):
            output.priority = priorities[index + 1]
    except ValueError:  # Should not happen
        pass


def ruleflow(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
    def package_initialisations(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

        def rule_decision_par_defaut(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            output.details.append("rule_decision_par_defaut")
            output.acknowledgement_to_requester = "#ACK"
            output.response_template_id = ""
            output.work_basket = work_basket_reorientation # Default work basket
            output.priority = "MEDIUM" # Default priority
            output.handling = "DEFLECTION" # Default handling

        def rule_other(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "other":
                output.details.append("rule_other")
                output.work_basket = work_basket_autres
                output.notes.append("#INTENTION_AUTRE")

        print(f"------- 📦 Executing package_initialisations")
        rule_decision_par_defaut(input, output)
        rule_other(input, output)



    def package_regles_nationales(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_depot_de_demande_d_asile_regle_nationale(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "depot_de_demande_d_asile":
                output.details.append("rule_depot_de_demande_d_asile_regle_nationale")
                text = "**Le site officiel de l'administration française** - Demande d'asile"
                url = "https://www.service-public.fr/particuliers/vosdroits/F2232#:~:text=Si%20vous%20souhaitez%20entrer%20en,de%20votre%20lieu%20d'arriv%C3%A9e."
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"

        def rule_ou_en_est_ma_demande_d_asile_en_cours(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "ou_en_est_ma_dem_asile_en_cours":
                output.details.append("ou_en_est_ma_dem_asile_en_cours")
                output.acknowledgement_to_requester = "#CONTACT_OFPRA"

        def rule_rdv_premiere_demande_titre_sejour(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "rdv_premiere_demande_titre_sejour":
                output.details.append("rule_rdv_premiere_demande_titre_sejour")
                text = "**Demande de rendez-vous** - Admission exceptionnelle au séjour"
                url = "https://www.demarches-simplifiees.fr/commencer/demande-de-rendez-vous-admission-exceptionnelle-au-sejour"
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                output.priority = "LOW"

        def rule_asile_hebergement_urgence(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "asile_hebergement_urgence":
                output.details.append("rule_asile_hebergement_urgence")
                output.handling = "DEFLECTION"
                output.work_basket = work_basket_reorientation
                output.priority = "HIGH"
                if input.field_values.get("demandeur_d_asile"):
                    text = "Le site de **l’Office Français de l’Immigration et de l’Intégration**"
                    url = "https://www.ofii.fr/"
                    output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                else:
                    output.acknowledgement_to_requester = "#APPEL_115"

        def rule_aide_financiere_demandeur_asile(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "aide_financiere_demandeur_asile":
                output.details.append("rule_aide_financiere_demandeur_asile")
                output.handling = "DEFLECTION"
                output.work_basket = work_basket_reorientation
                output.priority = "HIGH"
                if input.field_values.get("demandeur_d_asile"):
                    text = "Le site de **l’Office Français de l’Immigration et de l’Intégration**"
                    url = "https://www.ofii.fr/"
                    output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                else:
                    output.acknowledgement_to_requester = "#AUCUNE_SOLUTION"

        def rule_duplicata(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "duplicata":
                output.details.append("rule_duplicata")
                text = "**Administration numérique pour les étrangers en France**"
                url = "https://administration-etrangers-en-france.interieur.gouv.fr"
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"

        print(f"------- 📦 Executing package_regles_nationales")

        rule_depot_de_demande_d_asile_regle_nationale(input, output)
        rule_ou_en_est_ma_demande_d_asile_en_cours(input, output)
        rule_rdv_premiere_demande_titre_sejour(input, output)
        rule_asile_hebergement_urgence(input, output)
        rule_aide_financiere_demandeur_asile(input, output)
        rule_duplicata(input, output)



    def package_cas_nominal_78(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_depot_de_demande_d_asile_78(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "depot_de_demande_d_asile":
                output.details.append("rule_depot_de_demande_d_asile_78")  # Rule trace
                text = "**Les services de l'État dans les Yvelines** - Je demande l'asile en France"
                url = "https://www.yvelines.gouv.fr/Demarches/Accueil-des-etrangers-dans-les-Yvelines/Asile/Je-demande-l-asile-en-France"
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"

        def rule_refugie_ou_protege_subsidiaire(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "dem_retour_pays_motif_except" and input.field_values["refugie_ou_protege_subsidiaire"]:
                output.details.append("rule_refugie_ou_protege_subsidiaire")

                output.handling = "AGENT"
                output.acknowledgement_to_requester = "#ACK"
                output.response_template_id = response_template_id_sauf_conduits
                output.work_basket = work_basket_sauf_conduits
                output.priority = "HIGH"

        def rule_expiration_d_une_atda(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "expiration_d_une_atda":
                output.details.append("rule_expiration_d_une_atda")

                output.handling = "AGENT"
                output.acknowledgement_to_requester = "#ACK"
                output.response_template_id = response_template_id_atda
                output.work_basket = work_basket_atda
                output.priority = "HIGH"

        def rule_expiration_d_une_api_cas_nominal(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "expiration_d_une_api":
                output.details.append("rule_expiration_d_une_api_cas_nominal")

                output.handling = "AGENT"
                output.acknowledgement_to_requester = "#ACK"
                output.response_template_id = response_template_id_api_a_renouveler
                output.work_basket = work_basket_api_a_renouveler

        def rule_expiration_d_une_api_api_expiree(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "expiration_d_une_api" and (difference_in_days := jours_jusqu_a_date(input, "date_expiration_api")) <= 0:
                output.details.append("rule_expiration_d_une_api_api_expiree")
                output.priority = "VERY_HIGH"
                output.notes.append(f"#API_EXPIREE_DEPUIS_X_JOURS,{abs(difference_in_days)}")

        def rule_expiration_d_une_api_api_non_expiree(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "expiration_d_une_api" and (difference_in_days := jours_jusqu_a_date(input, "date_expiration_api")) > 0:
                output.details.append("rule_expiration_d_une_api_api_non_expiree")
                if difference_in_days <= 30:
                    output.priority = "HIGH"
                    output.notes.append(f"#API_VA_EXPIRER_DANS_X_JOURS,{difference_in_days}")
                elif difference_in_days <= 90:
                    output.priority = "MEDIUM"
                else:
                    output.priority = "LOW"

        def rule_difficulte_prise_rdv(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "difficulte_prise_rdv":
                output.details.append("rule_difficulte_prise_rdv")
                output.acknowledgement_to_requester = "#ACCUEIL"
                output.work_basket = work_basket_accueil
                output.priority = "LOW"

        def rule_rdv_sauf_conduit(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "rdv_sauf_conduit":
                output.details.append("rule_rdv_sauf_conduit")
                output.response_template_id = response_template_id_sauf_conduits
                if input.field_values["motif_deces"]:
                    output.priority = "HIGH"
                    output.work_basket = work_basket_asile_priorite
                else:
                    output.work_basket = work_basket_sauf_conduits
                    output.priority = "MEDIUM"

        def rule_rdv_remise_de_titre(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "rdv_remise_de_titre":
                text = "**Prendre un rendez-vous** - Les services de l'État dans les Yvelines"
                url = "https://www.yvelines.gouv.fr/Prendre-un-rendez-vous"
                output.details.append("rule_rdv_remise_de_titre")
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                output.priority = "LOW"

        def rule_rdv_renouvellement_recepisse(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "rdv_renouvellement_recepisse":
                output.details.append("rule_rdv_renouvellement_recepisse")

                difference_in_days: int = jours_jusqu_a_date(input, "date_expiration_recepisse")
                output.notes.append(f"#RECEPISSE_VA_EXPIRER_DANS_X_JOURS,{difference_in_days}")

                if difference_in_days > 30:
                    text = "**Demande de renouvellement de récépissé** - Saisine des services de l'Etat par voie électronique - Etrangers"
                    url = "https://contacts-demarches.interieur.gouv.fr/etrangers/renouvellement-recepisse/"
                    output.priority = "MEDIUM"
                    output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                else:
                    output.priority = "HIGH"
                    output.acknowledgement_to_requester = "#ACCUEIL"
                    output.work_basket = work_basket_accueil

        def rule_rdv_renouvellement_titre_sejour_hors_anef(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "rdv_renouvellement_titre_sejour_hors_anef":
                output.details.append("rule_rdv_renouvellement_titre_sejour_hors_anef")

                difference_in_days: int = jours_jusqu_a_date(input, "date_expiration_titre_sejour")
                if difference_in_days <= 0:
                    output.notes.append(f"#TITRE_SEJOUR_EXPIRE_DEPUIS_X_JOURS,{abs(difference_in_days)}")
                else:
                    output.notes.append(f"#TITRE_SEJOUR_VA_EXPIRER_DANS_X_JOURS,{difference_in_days}")

                if input.field_values["statut"] in ["étudiant", "visiteur", "conjoint_de_français", "parent_d_enfant_français_mineur", "citoyen_UE"]:
                    output.notes.append(f"#STATUT, {input.field_values['statut']}")
                    output.notes.append("#RELEVE_DE_L_ANEF")
                    output.priority = "MEDIUM"
                    text = "**Administration numérique pour les étrangers en France**"
                    url = "https://administration-etrangers-en-france.interieur.gouv.fr"
                    output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                elif difference_in_days > 60:
                    text = "**Prendre un rendez-vous** - Les services de l'État dans les Yvelines"
                    url = "https://www.yvelines.gouv.fr/Prendre-un-rendez-vous"
                    output.priority = "MEDIUM"
                    output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                else:
                    output.priority = "HIGH"
                    output.acknowledgement_to_requester = "#ACCUEIL"
                    output.work_basket = work_basket_accueil

        def rule_dem_en_rapport_dublin_en_cours(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "dem_en_rapport_dublin_en_cours":
                output.details.append("rule_dem_en_rapport_dublin_en_cours")
                output.acknowledgement_to_requester = "#ACK"
                output.work_basket = work_basket_dublin
                output.priority = "HIGH"
                output.response_template_id = response_template_id_dublin

        print(f"------- 📦 Executing package_cas_nominal_78")

        rule_depot_de_demande_d_asile_78(input, output)
        rule_refugie_ou_protege_subsidiaire(input, output)
        rule_expiration_d_une_atda(input, output)
        rule_expiration_d_une_api_cas_nominal(input, output)
        rule_expiration_d_une_api_api_expiree(input, output)
        rule_expiration_d_une_api_api_non_expiree(input, output)
        rule_difficulte_prise_rdv(input, output)
        rule_rdv_sauf_conduit(input, output)
        rule_rdv_remise_de_titre(input, output)
        rule_rdv_renouvellement_recepisse(input, output)
        rule_rdv_renouvellement_titre_sejour_hors_anef(input, output)
        rule_dem_en_rapport_dublin_en_cours(input, output)



    def package_reajustements_78(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_risque_sur_l_emploi(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.field_values["mention_de_risque_sur_l_emploi"]:
                output.details.append("rule_risque_sur_l_emploi")
                augmenter_niveau_priorite(output)

        print(f"------- 📦 Executing package_reajustements_78")

        rule_risque_sur_l_emploi(input, output)


    print(f"----- Entering ruleflow")

    package_initialisations(input, output)
    package_regles_nationales(input, output)
    if input.field_values["departement"] == "78":
        package_cas_nominal_78(input, output)
        package_reajustements_78(input, output)


class DecisionEngineDelphes(CaseHandlingDecisionEngine):

    def _decide(self, input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        # Random value that will be overwritten in the rules
        output: CaseHandlingDecisionOutput = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="N/A",
            response_template_id="N/A",
            work_basket="N/A",
            priority="VERY_LOW",
            notes=[],
            details=[])

        print(f"----- 🔍 Executing Delphes decision engine ruleflow for intention_id='{input.intention_id}'")
        ruleflow(input, output)

        return output


def visualize_ruleflow():
    """Affiche la structure hiérarchique du ruleflow"""
    import ast
    import inspect
    from pathlib import Path
    
    # Obtenir le code source de ce fichier
    source_file = Path(__file__).resolve()
    with open(source_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    tree = ast.parse(source_code)
    
    # Trouver la fonction ruleflow
    ruleflow_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'ruleflow':
            ruleflow_func = node
            break
    
    if not ruleflow_func:
        print("❌ Fonction ruleflow non trouvée")
        return
    
    # Extraire les packages et règles
    packages = []
    for stmt in ruleflow_func.body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name.startswith('package_'):
            package_name = stmt.name
            rules = []
            for package_stmt in stmt.body:
                if isinstance(package_stmt, ast.FunctionDef) and package_stmt.name.startswith('rule_'):
                    rules.append(package_stmt.name)
            packages.append((package_name, rules))
    
    # Extraire l'ordre d'exécution
    execution_order = []
    for stmt in ruleflow_func.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            if isinstance(stmt.value.func, ast.Name):
                execution_order.append(stmt.value.func.id)
        elif isinstance(stmt, ast.If):
            for if_stmt in stmt.body:
                if isinstance(if_stmt, ast.Expr) and isinstance(if_stmt.value, ast.Call):
                    if isinstance(if_stmt.value.func, ast.Name):
                        func_name = if_stmt.value.func.id
                        condition = ast.unparse(stmt.test) if hasattr(ast, 'unparse') else "condition"
                        execution_order.append(f"{func_name} [if {condition}]")
    
    # Affichage
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + " RULEFLOW - MOTEUR DE DÉCISION DELPHES" + " " * 20 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    print("┌─ 📋 STRUCTURE HIÉRARCHIQUE DES RÈGLES")
    print("│")
    
    for i, (package_name, rules) in enumerate(packages):
        is_last_package = (i == len(packages) - 1)
        package_connector = "└──" if is_last_package else "├──"
        
        package_display = package_name.replace("package_", "").replace("_", " ").title()
        print(f"│   {package_connector} 📦 {package_display}")
        print(f"│   {'    ' if is_last_package else '│   '}    ({package_name})")
        print(f"│   {'    ' if is_last_package else '│   '}")
        
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
    
    print("┌─ 🔄 ORDRE D'EXÉCUTION DES PACKAGES")
    print("│")
    for i, package in enumerate(execution_order, 1):
        print(f"│   {i}. {package}")
    print("│")
    print("└" + "─" * 78)
    print()
    
    total_rules = sum(len(rules) for _, rules in packages)
    print("┌─ 📊 STATISTIQUES")
    print("│")
    print(f"│   • Nombre de packages : {len(packages)}")
    print(f"│   • Nombre total de règles : {total_rules}")
    print(f"│   • Nombre d'étapes d'exécution : {len(execution_order)}")
    print("│")
    print("└" + "─" * 78)


if __name__ == "__main__":
    print("🔍 Visualisation du Ruleflow\n")
    visualize_ruleflow()
