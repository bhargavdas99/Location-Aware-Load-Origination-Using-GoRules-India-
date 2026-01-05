import zen

class LoanDecisionEngine:
    def __init__(self):
        # No loader needed since we feed JSON directly
        self.engine = zen.ZenEngine()

    def evaluate(self, rules_dict: dict, input_data: dict) -> dict:
        """
        Takes the rules as a dictionary (from DB) and 
        evaluates them against the input data.
        """
        # We use create_decision to wrap the dictionary so Zen understands 
        # it is the content, not a filename string.
        decision = self.engine.create_decision(rules_dict)
        return decision.evaluate(input_data)