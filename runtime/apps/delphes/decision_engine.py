from datetime import datetime
from typing import Literal

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput

work_basket_api_a_renouveler = "api-a-renouveler"
work_basket_generique = "generique"
work_basket_pref_etrangers_aes_salarie = "pref-etrangers-aes-salarie"
work_basket_reorientation = "reorientation"
work_basket_sauf_conduits = "sauf-conduits"
work_basket_ukraine = "ukraine"

response_template_id_sauf_conduits = "sauf-conduits"
response_template_id_api_a_renouveler = "api-a-renouveler"


def days_between(date_begin: str, date_end: str) -> int:
    """
    Returns the number of days between two dates in 'd/M/yyyy' format.
    The result is positive if date_end is after date_begin, negative otherwise.
    """
    fmt = "%d/%m/%Y"
    d1 = datetime.strptime(date_begin, fmt)
    d2 = datetime.strptime(date_end, fmt)
    return (d2 - d1).days


def jours_jusqu_a_expiration_api(input: CaseHandlingDecisionInput) -> int:
    date_demande = input.field_values["date_demande"]
    date_expiration_api = input.field_values["date_expiration_api"]
    return days_between(date_begin=date_demande, date_end=date_expiration_api)


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
            output.handling = "AGENT"
            output.acknowledgement_to_requester = "#ACK"
            output.response_template_id = ""
            output.work_basket = work_basket_generique
            output.priority = "MEDIUM"

        rule_decision_par_defaut(input, output)

    def package_regles_nationales(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_depot_de_demande_d_asile_regle_nationale(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            text = "**Le site officiel de l'administration française** - Demande d'asile"
            url = "https://www.service-public.fr/particuliers/vosdroits/F2232#:~:text=Si%20vous%20souhaitez%20entrer%20en,de%20votre%20lieu%20d'arriv%C3%A9e."

            if input.intention_id == "depot_de_demande_d_asile":
                output.details.append("rule_depot_de_demande_d_asile_regle_nationale")

                output.handling = "DEFLECTION"
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                output.response_template_id = ""
                output.work_basket = work_basket_reorientation
                output.priority = "MEDIUM"

        def rule_ou_en_est_ma_demande_d_asile_en_cours(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "ou_en_est_ma_dem_asile_en_cours":
                output.details.append("ou_en_est_ma_dem_asile_en_cours")

                output.handling = "DEFLECTION"
                output.acknowledgement_to_requester = "#CONTACT_OFPRA"
                output.response_template_id = ""
                output.work_basket = work_basket_reorientation
                output.priority = "MEDIUM"

        rule_depot_de_demande_d_asile_regle_nationale(input, output)
        rule_ou_en_est_ma_demande_d_asile_en_cours(input, output)

    def package_cas_nominal_78(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_depot_de_demande_d_asile_78(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            text = "**Les services de l'État dans les Yvelines** - Je demande l'asile en France"
            url = "https://www.yvelines.gouv.fr/Demarches/Accueil-des-etrangers-dans-les-Yvelines/Asile/Je-demande-l-asile-en-France"

            if input.intention_id == "depot_de_demande_d_asile":
                output.details.append("rule_depot_de_demande_d_asile_78")  # Rule trace

                output.handling = "DEFLECTION"
                output.acknowledgement_to_requester = f"#VISIT_PAGE,{text},{url}"
                output.response_template_id = ""
                output.work_basket = work_basket_reorientation
                output.priority = "MEDIUM"

        def rule_refugie_ou_protege_subsidiaire(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "dem_retour_pays_motif_except" and input.field_values["refugie_ou_protege_subsidiaire"]:
                output.details.append("rule_refugie_ou_protege_subsidiaire")

                output.handling = "AGENT"
                output.acknowledgement_to_requester = "#ACK"
                output.response_template_id = response_template_id_sauf_conduits
                output.work_basket = work_basket_sauf_conduits
                output.priority = "HIGH"

        def rule_expiration_d_une_api_cas_nominal(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "expiration_d_une_api":
                output.details.append("rule_expiration_d_une_api_cas_nominal")

                output.handling = "AGENT"
                output.acknowledgement_to_requester = "#ACK"
                output.response_template_id = response_template_id_api_a_renouveler
                output.work_basket = work_basket_api_a_renouveler

        def rule_expiration_d_une_api_api_expiree(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "expiration_d_une_api" and (difference_in_days := jours_jusqu_a_expiration_api(input)) <= 0:
                output.details.append("rule_expiration_d_une_api_api_expiree")

                output.priority = "VERY_HIGH"
                output.notes.append(f"#API_EXPIREE_DEPUIS_X_JOURS,{abs(difference_in_days)}")

        def rule_expiration_d_une_api_api_non_expiree(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

            if input.intention_id == "expiration_d_une_api" and (difference_in_days := jours_jusqu_a_expiration_api(input)) > 0:
                output.details.append("rule_expiration_d_une_api_api_non_expiree")

                if difference_in_days <= 30:
                    output.priority = "HIGH"
                    output.notes.append(f"#API_VA_EXPIRER_DANS_X_JOURS,{difference_in_days}")

                elif difference_in_days <= 90:
                    output.priority = "MEDIUM"

                else:
                    output.priority = "LOW"

        rule_depot_de_demande_d_asile_78(input, output)
        rule_refugie_ou_protege_subsidiaire(input, output)
        rule_expiration_d_une_api_cas_nominal(input, output)
        rule_expiration_d_une_api_api_expiree(input, output)
        rule_expiration_d_une_api_api_non_expiree(input, output)

    def package_reajustements_78(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
        def rule_risque_sur_l_emploi(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.field_values["mention_de_risque_sur_l_emploi"]:
                output.details.append("rule_risque_sur_l_emploi")
                augmenter_niveau_priorite(output)

        rule_risque_sur_l_emploi(input, output)

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

        ruleflow(input, output)

        return output
