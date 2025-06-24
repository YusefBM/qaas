from abc import ABC, abstractmethod
from typing import Dict

from .question import Question


class QuestionRepository(ABC):
    @abstractmethod
    def save(self, question: Question) -> None:
        pass

    @abstractmethod
    def find_by_id(self, question_id: int) -> Question | None:
        pass

    @abstractmethod
    def find_by_ids(self, question_ids: list[int]) -> Dict[int, Question]:
        pass
