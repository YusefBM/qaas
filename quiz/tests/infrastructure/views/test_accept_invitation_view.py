import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status
from voluptuous import MultipleInvalid

from quiz.application.accept_invitation.accept_invitation_response import AcceptInvitationResponse
from quiz.domain.invitation.invitation_already_accepted_exception import InvitationAlreadyAcceptedException
from quiz.domain.invitation.invitation_not_found_exception import InvitationNotFoundException
from quiz.domain.invitation.only_invited_user_can_accept_invitation_exception import (
    OnlyInvitedUserCanAcceptInvitationException,
)
from quiz.domain.participation.participation_already_exists_exception import ParticipationAlreadyExistsException
from quiz.infrastructure.views.accept_invitation_view import AcceptInvitationView
from user.domain.user import User


class TestAcceptInvitationView(unittest.TestCase):
    def setUp(self):
        self.invitation_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participation_id = UUID("11111111-2222-3333-4444-555555555555")
        self.quiz_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id
        self.mock_user.is_authenticated = True

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_command_handler = Mock()
        self.mock_schema = Mock()
        self.mock_logger = Mock()
        self.view = AcceptInvitationView(
            command_handler=self.mock_command_handler, schema=self.mock_schema, logger=self.mock_logger
        )

    def test_post_success(self):
        mock_response = AcceptInvitationResponse(
            message="Invitation accepted successfully",
            invitation_id=self.invitation_id,
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="JavaScript Fundamentals",
        )

        self.mock_command_handler.handle.return_value = mock_response
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Invitation accepted successfully")
        self.assertEqual(response.data["invitation_id"], str(self.invitation_id))
        self.assertEqual(response.data["participation_id"], str(self.participation_id))
        self.assertEqual(response.data["quiz_id"], str(self.quiz_id))
        self.assertEqual(response.data["quiz_title"], "JavaScript Fundamentals")

        self.mock_command_handler.handle.assert_called_once()
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.invitation_id, self.invitation_id)
        self.assertEqual(command_arg.user_id, self.user_id)

    def test_post_handles_invitation_not_found_exception(self):
        self.mock_command_handler.handle.side_effect = InvitationNotFoundException(str(self.invitation_id))
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Invitation with ID 12345678-1234-5678-9abc-123456789abc not found")

    def test_post_handles_only_invited_user_can_accept_exception(self):
        self.mock_command_handler.handle.side_effect = OnlyInvitedUserCanAcceptInvitationException(
            invitation_id=self.invitation_id, user_id=self.user_id
        )
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["message"],
            "User 87654321-4321-8765-cba9-987654321098 is not authorized to accept invitation 12345678-1234-5678-9abc-123456789abc",
        )

    def test_post_handles_invitation_already_accepted_exception(self):
        self.mock_command_handler.handle.side_effect = InvitationAlreadyAcceptedException(self.invitation_id)
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_handles_participation_already_exists_exception(self):
        self.mock_command_handler.handle.side_effect = ParticipationAlreadyExistsException(
            quiz_id=str(self.quiz_id), participant_id=str(self.user_id)
        )
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["message"],
            "Participation already exists for participant '87654321-4321-8765-cba9-987654321098' in quiz 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'",
        )

    def test_post_handles_validation_error(self):
        self.mock_schema.side_effect = MultipleInvalid("Invalid UUID format")

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The request is invalid", response.data["message"])

    def test_post_handles_value_error(self):
        self.mock_command_handler.handle.side_effect = ValueError("Invalid input")
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Invalid input")

    def test_post_handles_unexpected_exception(self):
        self.mock_command_handler.handle.side_effect = Exception("Unexpected error")
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when accepting invitation")

    def test_post_with_different_invitation_id(self):
        different_invitation_id = UUID("99999999-8888-7777-6666-555555555555")
        mock_response = AcceptInvitationResponse(
            message="Different invitation accepted",
            invitation_id=different_invitation_id,
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Python Advanced",
        )

        self.mock_command_handler.handle.return_value = mock_response
        self.mock_schema.return_value = {
            "invitation_id": different_invitation_id,
            "user_id": self.user_id,
        }

        response = self.view.post(self.mock_request, different_invitation_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invitation_id"], str(different_invitation_id))
        self.assertEqual(response.data["quiz_title"], "Python Advanced")

        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.invitation_id, different_invitation_id)

    def test_post_with_different_user(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id
        different_user.is_authenticated = True

        different_request = Mock()
        different_request.user = different_user

        mock_response = AcceptInvitationResponse(
            message="Invitation accepted by different user",
            invitation_id=self.invitation_id,
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Django Basics",
        )

        self.mock_command_handler.handle.return_value = mock_response
        self.mock_schema.return_value = {
            "invitation_id": self.invitation_id,
            "user_id": different_user_id,
        }

        response = self.view.post(different_request, self.invitation_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.user_id, different_user_id)
