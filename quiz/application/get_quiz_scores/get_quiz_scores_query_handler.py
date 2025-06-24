from logging import getLogger
from uuid import UUID

from quiz.application.get_quiz_scores.get_quiz_scores_query import GetQuizScoresQuery
from quiz.application.get_quiz_scores.get_quiz_scores_response import GetQuizScoresResponse
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.quiz.quiz_repository import QuizRepository
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class GetQuizScoresQueryHandler:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        participation_finder: ParticipationFinder,
    ) -> None:
        self.__quiz_repository = quiz_repository
        self.__participation_finder = participation_finder
        self.__logger = getLogger(__name__)

    def handle(self, query: GetQuizScoresQuery) -> GetQuizScoresResponse:
        self.__logger.info(f"Getting quiz scores for quiz '{query.quiz_id}'. Requested by user '{query.requester_id}'")

        quiz = self.__quiz_repository.find_or_fail_by_id(quiz_id=UUID(query.quiz_id))
        if str(quiz.creator_id) != str(query.requester_id):
            raise UnauthorizedQuizAccessException(quiz_id=str(query.quiz_id), user_id=str(query.requester_id))

        quiz_scores_summary = self.__participation_finder.find_quiz_scores_summary(quiz_id=UUID(query.quiz_id))

        self.__logger.info(
            f"Retrieved quiz scores summary for '{query.quiz_id}'. Requested by user '{query.requester_id}'"
        )

        return GetQuizScoresResponse(
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            total_participants=quiz_scores_summary.total_participants,
            average_score=quiz_scores_summary.average_score,
            max_score=quiz_scores_summary.max_score,
            min_score=quiz_scores_summary.min_score,
            top_scorer_email=quiz_scores_summary.top_scorer_email,
        )
