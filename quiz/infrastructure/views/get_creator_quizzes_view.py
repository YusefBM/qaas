from logging import getLogger
from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from quiz.application.get_creator_quizzes.get_creator_quizzes_query import GetCreatorQuizzesQuery
from quiz.application.get_creator_quizzes.get_creator_quizzes_query_handler_factory import (
    GetCreatorQuizzesQueryHandlerFactory,
)


class GetCreatorQuizzesView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__query_handler = GetCreatorQuizzesQueryHandlerFactory.create()
        self.__logger = getLogger(__name__)

    def get(self, request: Request, creator_id: UUID) -> Response:
        try:
            query = GetCreatorQuizzesQuery(
                creator_id=str(creator_id),
            )
            get_creator_quizzes_response = self.__query_handler.handle(query)

            return Response(get_creator_quizzes_response.as_dict(), status=status.HTTP_200_OK)

        except Exception as error:
            self.__logger.exception(f"Error getting user's quizzes: '{error}'")
            return Response(
                {"message": "Internal server error when getting user's quizzes"}, status=HTTP_500_INTERNAL_SERVER_ERROR
            )
