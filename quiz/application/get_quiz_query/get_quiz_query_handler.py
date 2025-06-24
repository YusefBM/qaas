from logging import getLogger
from uuid import UUID

from quiz.application.get_quiz_query.get_quiz_query import GetQuizQuery
from quiz.application.get_quiz_query.get_quiz_query_response import GetQuizQueryResponse
from quiz.application.get_quiz_query.quiz_data_mapper import QuizDataMapper
from quiz.domain.invitation.invitation_repository import InvitationRepository
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.quiz.quiz_data import QuizData
from quiz.domain.quiz.quiz_finder import QuizFinder
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class GetQuizQueryHandler:
    def __init__(
        self,
        quiz_finder: QuizFinder,
        participation_repository: ParticipationRepository,
        invitation_repository: InvitationRepository,
        mapper: QuizDataMapper,
    ) -> None:
        self.__quiz_finder = quiz_finder
        self.__participation_repository = participation_repository
        self.__invitation_repository = invitation_repository
        self.__mapper = mapper
        self.__logger = getLogger(__name__)

    def handle(self, query: GetQuizQuery) -> GetQuizQueryResponse:
        self.__logger.info(f"Processing quiz retrieval query - Quiz: {query.quiz_id}, User: {query.participant_id}")

        quiz_data = self.__quiz_finder.find_quiz_for_participation(
            quiz_id=query.quiz_id, participant_id=query.participant_id
        )

        self.__validate_authorization(quiz_data, query.participant_id)

        response = self.__mapper.map_to_response(quiz_data)

        self.__logger.info(f"Successfully retrieved quiz {query.quiz_id} for user {query.participant_id}")

        return response

    def __validate_authorization(self, quiz_data, participant_id) -> None:
        if not self.__is_authorized_to_view_quiz(quiz_data, participant_id):
            raise UnauthorizedQuizAccessException(quiz_id=str(quiz_data.quiz_id), user_id=str(participant_id))

    def __is_authorized_to_view_quiz(self, quiz_data: QuizData, participant_id: UUID) -> bool:
        if str(quiz_data.quiz_creator_id) == str(participant_id):
            return True

        if self.__participation_repository.exists_by_quiz_and_participant(quiz_data.quiz_id, participant_id):
            return True

        if self.__invitation_repository.exists_by_quiz_and_invited(
            quiz_id=quiz_data.quiz_id, invited_id=participant_id
        ):
            return True

        return False
