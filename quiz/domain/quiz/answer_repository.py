from abc import ABC, abstractmethod
from typing import Optional, Dict

from quiz.domain.quiz.answer import Answer


class AnswerRepository(ABC):
    @abstractmethod
    def save(self, answer: Answer) -> None:
        pass

    @abstractmethod
    def bulk_save(self, answers: list[Answer]) -> None:
        pass

    @abstractmethod
    def find_by_id(self, answer_id: int) -> Optional[Answer]:
        pass

    @abstractmethod
    def find_by_ids(self, answer_ids: list[int]) -> Dict[int, Answer]:
        pass
