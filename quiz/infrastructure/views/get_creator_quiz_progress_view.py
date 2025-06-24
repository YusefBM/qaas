from logging import getLogger, Logger
from typing import Optional
from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from rest_framework.views import APIView

from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query import GetCreatorQuizProgressQuery
from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query_handler import (
    GetCreatorQuizProgressQueryHandler,
)
from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query_handler_factory import (
    GetCreatorQuizProgressQueryHandlerFactory,
)
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class GetCreatorQuizProgressView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(
        self,
        query_handler: Optional[GetCreatorQuizProgressQueryHandler] = None,
        logger: Optional[Logger] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__query_handler = query_handler or GetCreatorQuizProgressQueryHandlerFactory.create()
        self.__logger = logger or getLogger(__name__)

    def get(self, request: Request, quiz_id: UUID) -> Response:
        try:
            query = GetCreatorQuizProgressQuery(
                quiz_id=str(quiz_id),
                requester_id=str(request.user.id),
            )
            get_creator_quiz_progress_response = self.__query_handler.handle(query)

            return Response(get_creator_quiz_progress_response.as_dict(), status=status.HTTP_200_OK)

        except QuizNotFoundException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_404_NOT_FOUND,
            )
        except UnauthorizedQuizAccessException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_403_FORBIDDEN,
            )
        except Exception as error:
            self.__logger.exception(f"Error getting creator quiz progress: '{error}'")
            return Response(
                {"message": "Internal server error when getting creator quiz progress"},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
