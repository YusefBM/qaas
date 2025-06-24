from quiz.application.get_user_quizzes.get_user_quizzes_query_handler import GetUserQuizzesQueryHandler
from quiz.infrastructure.db_participation_repository import DbParticipationRepository
from quiz.infrastructure.db_quiz_repository import DbQuizRepository


class GetUserQuizzesQueryHandlerFactory:
    @staticmethod
    def create() -> GetUserQuizzesQueryHandler:
        return GetUserQuizzesQueryHandler(
            quiz_repository=DbQuizRepository(),
            participation_repository=DbParticipationRepository(),
        )
