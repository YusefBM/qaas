from logging import getLogger
from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
)
from rest_framework.views import APIView
from voluptuous import MultipleInvalid

from quiz.application.accept_invitation.accept_invitation_command import AcceptInvitationCommand
from quiz.application.accept_invitation.accept_invitation_command_handler_factory import (
    AcceptInvitationCommandHandlerFactory,
)
from quiz.application.accept_invitation.accept_invitation_schema import accept_invitation_schema
from quiz.domain.invitation.invitation_already_accepted_exception import InvitationAlreadyAcceptedException
from quiz.domain.invitation.invitation_not_found_exception import InvitationNotFoundException
from quiz.domain.invitation.only_invited_user_can_accept_invitation_exception import (
    OnlyInvitedUserCanAcceptInvitationException,
)
from quiz.domain.participation.participation_already_exists_exception import ParticipationAlreadyExistsException


class AcceptInvitationView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__command_handler = AcceptInvitationCommandHandlerFactory.create()
        self.__schema = accept_invitation_schema
        self.__logger = getLogger(__name__)

    def post(self, request: Request, invitation_id: UUID) -> Response:
        try:
            user_id = UUID(str(request.user.id))

            request_data = {
                "invitation_id": invitation_id,
                "user_id": user_id,
            }
            validated_data = self.__schema(request_data)

            command = AcceptInvitationCommand(
                invitation_id=validated_data["invitation_id"],
                user_id=validated_data["user_id"],
            )

            accept_invitation_response = self.__command_handler.handle(command)

            return Response(accept_invitation_response.as_dict(), status=status.HTTP_200_OK)

        except MultipleInvalid as error:
            self.__logger.warning(f"Validation error for accepting invitation: '{error}'")
            return Response({"message": f"The request is invalid: {error}"}, status=HTTP_400_BAD_REQUEST)

        except ValueError as error:
            self.__logger.warning(f"Invalid request for accepting invitation: '{error}'")
            return Response({"message": str(error)}, status=HTTP_400_BAD_REQUEST)

        except InvitationNotFoundException as error:
            self.__logger.warning(f"Invitation not found: '{error}'")
            return Response({"message": str(error)}, status=HTTP_404_NOT_FOUND)

        except OnlyInvitedUserCanAcceptInvitationException as error:
            self.__logger.warning(f"Unauthorized invitation access: '{error}'")
            return Response({"message": str(error)}, status=HTTP_403_FORBIDDEN)

        except (InvitationAlreadyAcceptedException, ParticipationAlreadyExistsException) as error:
            self.__logger.warning(f"Resource conflict: '{error}'")
            return Response({"message": str(error)}, status=HTTP_409_CONFLICT)

        except Exception as error:
            self.__logger.exception(f"Error accepting invitation: '{error}'")
            return Response(
                {"message": "Internal server error when accepting invitation"}, status=HTTP_500_INTERNAL_SERVER_ERROR
            )
