from typing import List, Tuple


class Retriever:
    def __init__(self, vector_store) -> None:
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[float, dict]]:
        raise NotImplementedError(
            "Perform embedding of query and vector DB search."
        ) 