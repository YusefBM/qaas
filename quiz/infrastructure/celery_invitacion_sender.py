import logging
from uuid import UUID

from quiz.domain.invitation.invitation_sender import InvitationSender
from quiz.infrastructure.send_invitation_email_task import send_invitation_email_task

logger = logging.getLogger(__name__)


class CeleryInvitationSender(InvitationSender):
    def send_invitation_email(self, invitation_id: UUID, invitation_acceptance_link: str) -> None:
        send_invitation_email_task.delay(
            invitation_id=str(invitation_id),
            invitation_acceptance_link=invitation_acceptance_link,
        )
