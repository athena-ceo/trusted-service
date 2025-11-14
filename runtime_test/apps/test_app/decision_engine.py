from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput


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


class DecisionEngine(CaseHandlingDecisionEngine):
    def _decide(self, input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        output: CaseHandlingDecisionOutput = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="N/A",
            response_template_id="N/A",
            work_basket="N/A",
            priority="VERY_LOW",
            notes=[],
            details=[])

        print(f"----- 🔍 Executing test_app decision engine ruleflow for intention_id='{input.intention_id}'")
        ruleflow(input, output)

        return output