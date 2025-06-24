from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary
from quiz.domain.participation.quiz_progress_summary import QuizProgressSummary
from quiz.domain.participation.user_participation_data import UserParticipationData


class ParticipationFinder(ABC):
    @abstractmethod
    def find_quiz_scores_summary(self, quiz_id: UUID) -> QuizScoresSummary:
        pass

    @abstractmethod
    def find_creator_quiz_progress_summary(self, quiz_id: UUID) -> QuizProgressSummary:
        pass

    @abstractmethod
    def find_user_participation_for_quiz(self, quiz_id: UUID, user_id: UUID) -> Optional[UserParticipationData]:
        pass
