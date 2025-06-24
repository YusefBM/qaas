from logging import getLogger

from quiz.application.send_invitation_email.send_invitation_email_command import SendInvitationEmailCommand
from quiz.domain.invitation.email_service import EmailService
from quiz.domain.invitation.invitation_related_attribute import InvitationRelatedAttribute
from quiz.domain.invitation.invitation_repository import InvitationRepository


class SendInvitationEmailCommandHandler:
    def __init__(self, invitation_repository: InvitationRepository, email_service: EmailService):
        self.__invitation_repository = invitation_repository
        self.__email_service = email_service
        self.__logger = getLogger(__name__)

    def handle(self, command: SendInvitationEmailCommand) -> None:
        invitation = self.__invitation_repository.find_or_fail_by_id(
            command.invitation_id,
            related_attributes=[
                InvitationRelatedAttribute.QUIZ,
                InvitationRelatedAttribute.INVITED,
                InvitationRelatedAttribute.INVITER,
            ],
        )

        self.__email_service.send_invitation_email(invitation, command.invitation_acceptance_link)

        self.__logger.info(f"Email sending delegated to email service for invitation {command.invitation_id}")
