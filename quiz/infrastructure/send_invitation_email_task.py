from logging import getLogger
from uuid import UUID

from celery import shared_task

from quiz.application.send_invitation_email.send_invitation_email_command import SendInvitationEmailCommand
from quiz.application.send_invitation_email.send_invitation_email_command_handler_factory import (
    SendInvitationEmailCommandHandlerFactory,
)
from quiz.infrastructure.django_email_service import EmailDeliveryException

logger = getLogger(__name__)


@shared_task(autoretry_for=(EmailDeliveryException,), retry_kwargs={"countdown": 60, "max_retries": 3})
def send_invitation_email_task(invitation_id: str, invitation_acceptance_link: str) -> None:
    logger.info(f"Invitation email task initiated for invitation {invitation_id}")
    command = SendInvitationEmailCommand(
        invitation_id=UUID(invitation_id), invitation_acceptance_link=invitation_acceptance_link
    )
    command_handler = SendInvitationEmailCommandHandlerFactory.create()
    command_handler.handle(command)

    logger.info(f"Invitation email task completed for invitation {invitation_id}")
