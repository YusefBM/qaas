from logging import getLogger
from uuid import UUID

from quiz.application.get_user_quiz_progress.get_user_quiz_progress_query import GetUserQuizProgressQuery
from quiz.application.get_user_quiz_progress.get_user_quiz_progress_response import (
    GetUserQuizProgressResponse,
    ParticipationData,
)
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.participation.participation_not_found_for_user_exception import ParticipationNotFoundForUserException
from quiz.domain.quiz.quiz_repository import QuizRepository


class GetUserQuizProgressQueryHandler:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        participation_finder: ParticipationFinder,
    ) -> None:
        self.__quiz_repository = quiz_repository
        self.__participation_finder = participation_finder
        self.__logger = getLogger(__name__)

    def handle(self, query: GetUserQuizProgressQuery) -> GetUserQuizProgressResponse:
        self.__logger.info(
            f"Getting user quiz progress for quiz '{query.quiz_id}'. Requested by user '{query.requester_id}'"
        )

        quiz = self.__quiz_repository.find_or_fail_by_id(quiz_id=UUID(query.quiz_id))

        user_participation = self.__participation_finder.find_user_participation_for_quiz(
            quiz_id=UUID(query.quiz_id), user_id=UUID(query.requester_id)
        )
        if user_participation is None:
            raise ParticipationNotFoundForUserException(quiz_id=query.quiz_id, user_id=query.requester_id)

        score_percentage = None
        if user_participation.score is not None and quiz.total_possible_points > 0:
            score_percentage = (user_participation.score / quiz.total_possible_points) * 100

        participation = ParticipationData(
            status=user_participation.status,
            invited_at=user_participation.invited_at,
            completed_at=user_participation.completed_at,
            score=user_participation.score,
            score_percentage=round(score_percentage, 2) if score_percentage is not None else None,
        )

        self.__logger.info(
            f"Retrieved user quiz progress for '{query.quiz_id}'. Requested by user '{query.requester_id}'"
        )

        return GetUserQuizProgressResponse(
            quiz_id=str(quiz.id),
            quiz_title=quiz.title,
            quiz_description=quiz.description,
            total_questions=quiz.total_questions,
            total_possible_points=quiz.total_possible_points,
            quiz_created_at=quiz.get_formatted_created_at(),
            participation=participation,
        )
