from quiz.application.send_invitation_email.send_invitation_email_command_handler import (
    SendInvitationEmailCommandHandler,
)
from quiz.infrastructure.db_invitation_repository import DbInvitationRepository
from quiz.infrastructure.django_email_service import DjangoEmailService


class SendInvitationEmailCommandHandlerFactory:
    @staticmethod
    def create() -> SendInvitationEmailCommandHandler:
        return SendInvitationEmailCommandHandler(
            invitation_repository=DbInvitationRepository(),
            email_service=DjangoEmailService(),
        )
