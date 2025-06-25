from abc import ABC, abstractmethod
from uuid import UUID

from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_related_attribute import ParticipationRelatedAttribute


class ParticipationRepository(ABC):
    @abstractmethod
    def find_all_by_user_id(
        self, user_id: UUID, related_attributes: list[ParticipationRelatedAttribute] | None = None
    ) -> list[Participation]:
        pass

    @abstractmethod
    def find_or_fail_by_quiz_and_participant(self, quiz_id: UUID, participant_id: UUID) -> Participation:
        pass

    @abstractmethod
    def save(self, participation: Participation) -> None:
        pass

    @abstractmethod
    def exists_by_quiz_and_participant(self, quiz_id: UUID, participant_id: UUID) -> bool:
        pass
