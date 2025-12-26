import zen


def gorules_loader(key: str) -> str:
    with open(key, "r") as f:
        return f.read()


class LoanDecisionEngine:
    def __init__(self):
        self.engine = zen.ZenEngine({"loader": gorules_loader})

    def evaluate(self, rules_path: str, input_data: dict) -> dict:
        return self.engine.evaluate(rules_path, input_data)
