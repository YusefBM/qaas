from abc import ABC, abstractmethod
from uuid import UUID

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_related_attribute import InvitationRelatedAttribute


class InvitationRepository(ABC):
    @abstractmethod
    def find_or_fail_by_id(
        self, invitation_id: UUID, related_attributes: list[InvitationRelatedAttribute] | None = None
    ) -> Invitation:
        pass

    @abstractmethod
    def find_active_invitation(self, quiz_id: UUID, participant_id: UUID) -> Invitation | None:
        pass

    @abstractmethod
    def save(self, invitation: Invitation) -> None:
        pass

    @abstractmethod
    def exists_by_quiz_and_invited(self, quiz_id: UUID, invited_id: UUID) -> bool:
        pass
