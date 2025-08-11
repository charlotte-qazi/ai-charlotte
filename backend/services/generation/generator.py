from typing import List, Optional


class AnswerGenerator:
    def __init__(self, api_key: Optional[str], model: str = "gpt-3.5-turbo") -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, question: str, contexts: List[dict]) -> str:
        raise NotImplementedError(
            "Call LLM to generate an answer using retrieved contexts."
        ) 