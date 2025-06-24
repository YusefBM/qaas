from abc import ABC, abstractmethod
from uuid import UUID

from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary


class ParticipationFinder(ABC):
    @abstractmethod
    def find_quiz_scores_summary(self, quiz_id: UUID) -> QuizScoresSummary:
        pass
