from quiz.application.get_quiz_scores.get_quiz_scores_query_handler import GetQuizScoresQueryHandler
from quiz.infrastructure.db_participation_finder import DbParticipationFinder
from quiz.infrastructure.db_quiz_repository import DbQuizRepository


class GetQuizScoresQueryHandlerFactory:
    @staticmethod
    def create() -> GetQuizScoresQueryHandler:
        return GetQuizScoresQueryHandler(
            quiz_repository=DbQuizRepository(),
            participation_finder=DbParticipationFinder(),
        )
