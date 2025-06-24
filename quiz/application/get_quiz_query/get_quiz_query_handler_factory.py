from quiz.application.get_quiz_query.get_quiz_query_handler import GetQuizQueryHandler
from quiz.application.get_quiz_query.quiz_data_mapper import QuizDataMapper
from quiz.infrastructure.db_quiz_finder import DbQuizFinder
from quiz.infrastructure.db_participation_repository import DbParticipationRepository
from quiz.infrastructure.db_invitation_repository import DbInvitationRepository


class GetQuizQueryHandlerFactory:

    @staticmethod
    def create() -> GetQuizQueryHandler:
        return GetQuizQueryHandler(
            quiz_finder=DbQuizFinder(),
            participation_repository=DbParticipationRepository(),
            invitation_repository=DbInvitationRepository(),
            mapper=QuizDataMapper(),
        )
