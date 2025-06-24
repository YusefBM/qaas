from logging import getLogger

from quiz.application.get_user_quizzes.get_user_quizzes_query import GetUserQuizzesQuery
from quiz.application.get_user_quizzes.get_user_quizzes_response import GetUserQuizzesResponse, QuizParticipationSummary
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_related_attribute import ParticipationRelatedAttribute
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.quiz.quiz_repository import QuizRepository


class GetUserQuizzesQueryHandler:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        participation_repository: ParticipationRepository,
    ) -> None:
        self.__quiz_repository = quiz_repository
        self.__participation_repository = participation_repository
        self.__logger = getLogger(__name__)

    def handle(self, query: GetUserQuizzesQuery) -> GetUserQuizzesResponse:
        user_id = query.requester_id
        self.__logger.info(f"Getting quizzes for user '{user_id}'")

        participations = self.__participation_repository.find_all_by_user_id(
            user_id=user_id, related_attributes=[ParticipationRelatedAttribute.QUIZ]
        )

        participation_summaries = self.__get_participation_summaries(participations)

        self.__logger.info(f"Retrieved {len(participation_summaries)} quizzes for user '{user_id}'")

        return GetUserQuizzesResponse(
            quizzes_participations=participation_summaries,
            total_count=len(participation_summaries),
        )

    def __get_participation_summaries(self, participations: list[Participation]) -> list[QuizParticipationSummary]:
        participation_summaries = []
        for participation in participations:
            quiz = participation.quiz
            participation_summaries.append(
                QuizParticipationSummary(
                    quiz_id=quiz.id,
                    quiz_title=quiz.title,
                    quiz_description=quiz.description,
                    total_questions=quiz.total_questions,
                    total_participants=quiz.total_participants,
                    quiz_created_at=quiz.get_formatted_created_at(),
                    score=participation.score,
                    completed_at=participation.get_formatted_completed_at(),
                    participation_status=participation.status,
                    participation_created_at=participation.get_formatted_created_at(),
                )
            )

        return participation_summaries
