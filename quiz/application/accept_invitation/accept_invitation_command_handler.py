from logging import getLogger

from django.db import transaction
from uuid_utils.compat import uuid7

from quiz.application.accept_invitation.accept_invitation_command import AcceptInvitationCommand
from quiz.application.accept_invitation.accept_invitation_response import AcceptInvitationResponse
from quiz.domain.invitation.invitation_already_accepted_exception import InvitationAlreadyAcceptedException
from quiz.domain.invitation.invitation_repository import InvitationRepository
from quiz.domain.invitation.only_invited_user_can_accept_invitation_exception import (
    OnlyInvitedUserCanAcceptInvitationException,
)
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_repository import ParticipationRepository


class AcceptInvitationCommandHandler:
    def __init__(
        self,
        invitation_repository: InvitationRepository,
        participation_repository: ParticipationRepository,
    ) -> None:
        self.__invitation_repository = invitation_repository
        self.__participation_repository = participation_repository
        self.__logger = getLogger(__name__)

    def handle(self, command: AcceptInvitationCommand) -> AcceptInvitationResponse:
        self.__logger.info(
            f"Processing invitation acceptance. Invitation ID: '{command.invitation_id}', Participant ID: '{command.user_id}'"
        )
        invitation = self.__invitation_repository.find_or_fail_by_id(command.invitation_id)

        if not invitation.can_be_accepted_by(command.user_id):
            raise OnlyInvitedUserCanAcceptInvitationException(command.invitation_id, command.user_id)

        if invitation.is_accepted():
            raise InvitationAlreadyAcceptedException(command.invitation_id)

        invitation.accept()
        participation = Participation(
            id=uuid7(),
            quiz=invitation.quiz,
            participant=invitation.invited,
            invitation=invitation,
        )

        with transaction.atomic():
            self.__invitation_repository.save(invitation)
            self.__participation_repository.save(participation)

        self.__logger.info(
            f"Invitation accepted successfully. Invitation ID: '{command.invitation_id}', "
            f"Participation created with ID: {participation.id}"
        )

        return AcceptInvitationResponse(
            message="Invitation accepted successfully",
            invitation_id=invitation.id,
            participation_id=participation.id,
            quiz_id=invitation.quiz.id,
            quiz_title=invitation.quiz.title,
        )
