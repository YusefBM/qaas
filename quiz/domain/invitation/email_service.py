from abc import ABC, abstractmethod

from quiz.domain.invitation.invitation import Invitation


class EmailService(ABC):
    @abstractmethod
    def send_invitation_email(self, invitation: Invitation, invitation_acceptance_link: str) -> None:
        pass
