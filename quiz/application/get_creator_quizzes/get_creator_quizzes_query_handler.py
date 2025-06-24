from logging import getLogger
from uuid import UUID

from quiz.application.get_creator_quizzes.get_creator_quizzes_query import GetCreatorQuizzesQuery
from quiz.application.get_creator_quizzes.get_creator_quizzes_response import GetCreatorQuizzesResponse, QuizSummary
from quiz.domain.quiz.quiz_repository import QuizRepository


class GetCreatorQuizzesQueryHandler:
    __UTC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, quiz_repository: QuizRepository) -> None:
        self.__quiz_repository = quiz_repository
        self.__logger = getLogger(__name__)

    def handle(self, query: GetCreatorQuizzesQuery) -> GetCreatorQuizzesResponse:
        self.__logger.info(f"Getting quizzes for creator '{query.creator_id}'")

        quizzes = self.__quiz_repository.find_by_creator_id(creator_id=UUID(query.creator_id))

        quiz_summaries = []
        for quiz in quizzes:
            quiz_summaries.append(
                QuizSummary(
                    id=quiz.id,
                    title=quiz.title,
                    description=quiz.description,
                    questions_count=quiz.total_questions,
                    participants_count=quiz.total_participants,
                    created_at=quiz.created_at.strftime(self.__UTC_DATETIME_FORMAT),
                    updated_at=quiz.updated_at.strftime(self.__UTC_DATETIME_FORMAT),
                )
            )

        self.__logger.info(f"Retrieved {len(quiz_summaries)} quizzes for creator '{query.creator_id}'")

        return GetCreatorQuizzesResponse(
            creator_id=query.creator_id,
            quizzes=quiz_summaries,
            total_count=len(quiz_summaries),
        )
