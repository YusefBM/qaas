from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query_handler import (
    GetCreatorQuizProgressQueryHandler,
)
from quiz.infrastructure.db_participation_finder import DbParticipationFinder
from quiz.infrastructure.db_quiz_repository import DbQuizRepository


class GetCreatorQuizProgressQueryHandlerFactory:
    @staticmethod
    def create() -> GetCreatorQuizProgressQueryHandler:
        return GetCreatorQuizProgressQueryHandler(
            quiz_repository=DbQuizRepository(),
            participation_finder=DbParticipationFinder(),
        )
