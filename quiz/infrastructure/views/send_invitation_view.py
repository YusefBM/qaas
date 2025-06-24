from logging import getLogger, Logger
from typing import Optional

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
)
from rest_framework.views import APIView
from voluptuous import MultipleInvalid, Schema

from quiz.application.send_invitation.send_invitation_command import SendInvitationCommand
from quiz.application.send_invitation.send_invitation_command_handler import SendInvitationCommandHandler
from quiz.application.send_invitation.send_invitation_command_handler_factory import SendInvitationCommandHandlerFactory
from quiz.domain.invitation.invitation_already_exists_exception import InvitationAlreadyExistsException
from quiz.domain.invitation.only_quiz_creator_can_send_invitation_exception import (
    OnlyQuizCreatorCanSendInvitationException,
)
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.views.send_invitation_view_schema import send_invitation_view_schema
from user.domain.user_not_found_exception import UserNotFoundException


class SendInvitationView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(
        self,
        command_handler: Optional[SendInvitationCommandHandler] = None,
        schema: Optional[Schema] = None,
        logger: Optional[Logger] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__command_handler = command_handler or SendInvitationCommandHandlerFactory.create()
        self.__schema = schema or send_invitation_view_schema
        self.__logger = logger or getLogger(__name__)

    def post(self, request: Request, quiz_id: str) -> Response:
        try:
            validated_body = self.__get_validated_request_body(request.data)
        except MultipleInvalid as error:
            return Response(
                {"message": f"The request body is invalid: {error}"},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            command = SendInvitationCommand(
                quiz_id=quiz_id,
                participant_email=validated_body["participant_email"],
                inviter_id=str(request.user.id),
                inviter_email=request.user.email,
            )

            send_invitation_response = self.__command_handler.handle(command)

            return Response(send_invitation_response.as_dict(), status=HTTP_201_CREATED)

        except QuizNotFoundException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except UserNotFoundException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except OnlyQuizCreatorCanSendInvitationException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_403_FORBIDDEN,
            )
        except InvitationAlreadyExistsException as error:
            self.__logger.warning(f"Invitation already exists: '{error}'")
            return Response(
                {"message": f"{error}"},
                status=HTTP_409_CONFLICT,
            )
        except Exception as error:
            self.__logger.exception(f"Error sending invitation: '{error}'")
            return Response(
                {"message": "Internal server error when sending invitation"}, status=HTTP_500_INTERNAL_SERVER_ERROR
            )

    def __get_validated_request_body(self, request_body: dict) -> dict:
        return self.__schema(request_body)
