from logging import getLogger

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from quiz.application.get_user_quizzes.get_user_quizzes_query import GetUserQuizzesQuery
from quiz.application.get_user_quizzes.get_user_quizzes_query_handler_factory import GetUserQuizzesQueryHandlerFactory
from user.domain.user_not_found_exception import UserNotFoundException


class GetUserQuizzesView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__query_handler = GetUserQuizzesQueryHandlerFactory.create()
        self.__logger = getLogger(__name__)

    def get(self, request: Request) -> Response:
        try:
            query = GetUserQuizzesQuery(
                requester_id=request.user.id,
            )
            get_user_quizzes_response = self.__query_handler.handle(query)

            return Response(get_user_quizzes_response.as_dict(), status=status.HTTP_200_OK)

        except UserNotFoundException as error:
            self.__logger.warning(f"User not found when getting user's quizzes: '{error}'")
            return Response(
                {"message": f"User with id '{error.user_id}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as error:
            self.__logger.exception(f"Error getting user's quizzes: '{error}'")
            return Response(
                {"message": "Internal server error when getting user's quizzes"},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
