from quiz.application.get_creator_quizzes.get_creator_quizzes_query_handler import GetCreatorQuizzesQueryHandler
from quiz.infrastructure.db_quiz_repository import DbQuizRepository


class GetCreatorQuizzesQueryHandlerFactory:
    @staticmethod
    def create() -> GetCreatorQuizzesQueryHandler:
        quiz_repository = DbQuizRepository()
        return GetCreatorQuizzesQueryHandler(quiz_repository=quiz_repository)
