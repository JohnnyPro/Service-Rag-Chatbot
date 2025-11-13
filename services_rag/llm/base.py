# llm/base.py
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, q: str, relevant_document: str) -> str:
        pass
