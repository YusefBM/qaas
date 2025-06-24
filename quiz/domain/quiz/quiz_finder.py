from abc import ABC, abstractmethod
from uuid import UUID

from quiz.domain.quiz.quiz_data import QuizData


class QuizFinder(ABC):
    @abstractmethod
    def find_quiz_for_participation(self, quiz_id: UUID, participant_id: UUID) -> QuizData:
        pass
