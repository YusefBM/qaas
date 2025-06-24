from quiz.application.accept_invitation.accept_invitation_command_handler import AcceptInvitationCommandHandler
from quiz.infrastructure.db_invitation_repository import DbInvitationRepository
from quiz.infrastructure.db_participation_repository import DbParticipationRepository


class AcceptInvitationCommandHandlerFactory:
    @staticmethod
    def create() -> AcceptInvitationCommandHandler:
        return AcceptInvitationCommandHandler(
            invitation_repository=DbInvitationRepository(),
            participation_repository=DbParticipationRepository(),
        )
