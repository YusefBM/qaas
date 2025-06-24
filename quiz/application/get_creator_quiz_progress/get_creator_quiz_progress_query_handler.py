from logging import getLogger
from uuid import UUID

from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query import GetCreatorQuizProgressQuery
from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_response import GetCreatorQuizProgressResponse
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.quiz.quiz_repository import QuizRepository
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class GetCreatorQuizProgressQueryHandler:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        participation_finder: ParticipationFinder,
    ) -> None:
        self.__quiz_repository = quiz_repository
        self.__participation_finder = participation_finder
        self.__logger = getLogger(__name__)

    def handle(self, query: GetCreatorQuizProgressQuery) -> GetCreatorQuizProgressResponse:
        self.__logger.info(
            f"Getting creator quiz progress for quiz '{query.quiz_id}'. Requested by user '{query.requester_id}'"
        )

        quiz = self.__quiz_repository.find_or_fail_by_id(quiz_id=UUID(query.quiz_id))
        if str(quiz.creator_id) != str(query.requester_id):
            raise UnauthorizedQuizAccessException(quiz_id=str(query.quiz_id), user_id=str(query.requester_id))

        quiz_progress_summary = self.__participation_finder.find_creator_quiz_progress_summary(
            quiz_id=UUID(query.quiz_id)
        )

        self.__logger.info(
            f"Retrieved creator quiz progress summary for '{query.quiz_id}'. Requested by user '{query.requester_id}'"
        )

        return GetCreatorQuizProgressResponse(
            quiz_id=str(quiz.id),
            quiz_title=quiz.title,
            quiz_description=quiz.description,
            total_questions=quiz.total_questions,
            created_at=quiz.get_formatted_created_at(),
            invitation_stats=quiz_progress_summary.invitation_stats,
            participation_stats=quiz_progress_summary.participation_stats,
        )
