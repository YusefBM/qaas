from quiz.application.get_user_quiz_progress.get_user_quiz_progress_query_handler import GetUserQuizProgressQueryHandler
from quiz.infrastructure.db_participation_finder import DbParticipationFinder
from quiz.infrastructure.db_quiz_repository import DbQuizRepository


class GetUserQuizProgressQueryHandlerFactory:
    @staticmethod
    def create() -> GetUserQuizProgressQueryHandler:
        return GetUserQuizProgressQueryHandler(
            quiz_repository=DbQuizRepository(),
            participation_finder=DbParticipationFinder(),
        )
