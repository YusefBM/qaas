from abc import ABC, abstractmethod
from uuid import UUID


class InvitationSender(ABC):
    @abstractmethod
    def send_invitation_email(self, invitation_id: UUID, invitation_acceptance_link: str) -> None:
        pass
