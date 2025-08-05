from datetime import datetime
from typing import Literal

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput

work_basket_all_issues = "all_issues"


def increment_priority_level(output: CaseHandlingDecisionOutput):
    priorities: list[Literal["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]] = ["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    try:
        index = priorities.index(output.priority)
        if index + 1 < len(priorities):
            output.priority = priorities[index + 1]
    except ValueError:  # Should not happen
        pass


def ruleflow(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

    def package_initialisations(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

        def rule_default(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            output.details.append("rule_decision_par_defaut")

            output.handling = "AGENT"
            output.acknowledgement_to_requester = "#ACK"
            output.response_template_id = ""
            output.work_basket = work_basket_all_issues
            output.priority = "MEDIUM"

        rule_default(input, output)

    def package_standard_priority(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

        def rule_standard_billing_issues(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "billing_issues":
                output.details.append("rule_standard_billing_issues")

                output.priority = "VERY_LOW"

        def rule_standard_network_problems(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "network_problems":
                output.details.append("rule_standard_network_problems")

                output.priority = "LOW"

        def rule_standard_plan_changes(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "plan_changes":
                output.details.append("rule_standard_plan_changes")

                output.priority = "MEDIUM"

        def rule_standard_sim_or_device_support(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "sim_or_device_support":
                output.details.append("rule_standard_sim_or_device_support")

                output.priority = "HIGH"

        def rule_standard_account_management(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.intention_id == "account_management":
                output.details.append("rule_standard_account_management")

                output.priority = "VERY_HIGH"

        rule_standard_billing_issues(input, output)
        rule_standard_network_problems(input, output)
        rule_standard_plan_changes(input, output)
        rule_standard_sim_or_device_support(input, output)
        rule_standard_account_management(input, output)

    def package_particular_cases(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

        def rule_frustration_3(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.field_values["level_of_frustration"] == 3:
                output.details.append("rule_frustration_3")

                increment_priority_level(output)

        def rule_frustration_4(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.field_values["level_of_frustration"] == 4:
                output.details.append("rule_frustration_4")

                increment_priority_level(output)
                increment_priority_level(output)

        def rule_frustration_5(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.field_values["level_of_frustration"] == 5:
                output.details.append("rule_frustration_5")

                increment_priority_level(output)
                increment_priority_level(output)
                increment_priority_level(output)

        rule_frustration_3(input, output)
        rule_frustration_4(input, output)
        rule_frustration_5(input, output)

    def package_alerts(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):

        def rule_high_cltv_and_frustrated(input: CaseHandlingDecisionInput, output: CaseHandlingDecisionOutput):
            if input.field_values["level_of_frustration"] >= 3 and input.field_values["customer_lifetime_value"] >= "High":
                output.details.append("rule_high_cltv_and_frustrated")

                output.notes.append("#CLIENT_FRUSTRATED")
                output.notes.append("#CLIENT_HIGH_VALUE")

        rule_high_cltv_and_frustrated(input, output)


    package_initialisations(input, output)
    package_standard_priority(input, output)
    package_particular_cases(input, output)
    package_alerts(input, output)


class CaseHandlingDecisionEngineConnexionPython(CaseHandlingDecisionEngine):

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
