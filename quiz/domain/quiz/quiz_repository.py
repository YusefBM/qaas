from abc import ABC, abstractmethod
from uuid import UUID

from .quiz import Quiz


class QuizRepository(ABC):
    @abstractmethod
    def save(self, quiz: Quiz) -> None:
        pass

    @abstractmethod
    def find_or_fail_by_id(self, quiz_id: UUID) -> Quiz:
        pass

    @abstractmethod
    def find_by_creator_id(self, creator_id: UUID) -> list[Quiz]:
        pass

    @abstractmethod
    def find_by_participant_id(self, participant_id: UUID) -> list[Quiz]:
        pass
