from logging import getLogger

from django.conf import settings
from django.db import transaction
from uuid_utils.compat import uuid7

from quiz.application.send_invitation.send_invitation_command import SendInvitationCommand
from quiz.application.send_invitation.send_invitation_response import SendInvitationResponse
from quiz.domain.invitation.creator_cannot_be_invited_exception import CreatorCannotBeInvitedException
from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_repository import InvitationRepository
from quiz.domain.invitation.invitation_sender import InvitationSender
from quiz.domain.invitation.only_quiz_creator_can_send_invitation_exception import (
    OnlyQuizCreatorCanSendInvitationException,
)
from quiz.domain.quiz.quiz_repository import QuizRepository
from user.domain.user_repository import UserRepository


class SendInvitationCommandHandler:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        invitation_repository: InvitationRepository,
        user_repository: UserRepository,
        invitation_sender: InvitationSender,
    ):
        self.__quiz_repository = quiz_repository
        self.__invitation_repository = invitation_repository
        self.__user_repository = user_repository
        self.__invitation_sender = invitation_sender
        self.__logger = getLogger(__name__)

    def handle(self, command: SendInvitationCommand) -> SendInvitationResponse:
        if command.participant_email == command.inviter_email:
            raise CreatorCannotBeInvitedException(quiz_id=command.quiz_id, creator_id=command.inviter_id)

        quiz = self.__quiz_repository.find_or_fail_by_id(command.quiz_id)
        if str(quiz.creator.id) != command.inviter_id:
            raise OnlyQuizCreatorCanSendInvitationException(quiz_id=quiz.id, user_id=command.inviter_id)

        invited = self.__user_repository.find_or_fail_by_email(command.participant_email)

        invitation = Invitation(id=uuid7(), quiz=quiz, invited=invited, inviter_id=command.inviter_id)
        invitation_acceptance_link = f"{settings.BASE_URL}/invitations/{invitation.id}/accept"

        with transaction.atomic():
            self.__invitation_repository.save(invitation)
            self.__invitation_sender.send_invitation_email(
                invitation_id=invitation.id,
                invitation_acceptance_link=invitation_acceptance_link,
            )

        self.__logger.info(f"Invitation created and email queued for {command.participant_email} for quiz {quiz.title}")

        return SendInvitationResponse(
            invitation_id=str(invitation.id),
            quiz_title=quiz.title,
            participant_email=command.participant_email,
            invited_at=invitation.invited_at,
            invitation_acceptance_link=invitation_acceptance_link,
        )
