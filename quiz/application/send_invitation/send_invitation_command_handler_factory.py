from quiz.application.send_invitation.send_invitation_command_handler import SendInvitationCommandHandler
from quiz.infrastructure.celery_invitacion_sender import CeleryInvitationSender
from quiz.infrastructure.db_invitation_repository import DbInvitationRepository
from quiz.infrastructure.db_quiz_repository import DbQuizRepository
from user.infrastructure.db_user_repository import DbUserRepository


class SendInvitationCommandHandlerFactory:
    @staticmethod
    def create() -> SendInvitationCommandHandler:

        return SendInvitationCommandHandler(
            quiz_repository=DbQuizRepository(),
            invitation_repository=DbInvitationRepository(),
            user_repository=DbUserRepository(),
            invitation_sender=CeleryInvitationSender(),
        )
