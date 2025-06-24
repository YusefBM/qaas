import logging
from logging import Logger
from typing import Optional
from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from quiz.application.get_quiz_query.get_quiz_query import GetQuizQuery
from quiz.application.get_quiz_query.get_quiz_query_handler import GetQuizQueryHandler
from quiz.application.get_quiz_query.get_quiz_query_handler_factory import GetQuizQueryHandlerFactory
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class GetQuizView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(
        self, query_handler: Optional[GetQuizQueryHandler] = None, logger: Optional[Logger] = None, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__query_handler = query_handler or GetQuizQueryHandlerFactory.create()
        self.__logger = logger or logging.getLogger(__name__)

    def get(self, request: Request, quiz_id: UUID) -> Response:
        try:
            query = GetQuizQuery(
                participant_id=request.user.id,
                quiz_id=quiz_id,
            )
            response = self.__query_handler.handle(query)

            return Response(response.as_dict(), status=status.HTTP_200_OK)
        except UnauthorizedQuizAccessException as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as error:
            self.__logger.exception(f"Error getting user's quiz: '{error}'")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
