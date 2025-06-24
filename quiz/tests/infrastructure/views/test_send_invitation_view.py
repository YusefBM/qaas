import unittest
from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status
from voluptuous import MultipleInvalid

from quiz.application.send_invitation.send_invitation_response import SendInvitationResponse
from quiz.domain.invitation.invitation_already_exists_exception import InvitationAlreadyExistsException
from quiz.domain.invitation.only_quiz_creator_can_send_invitation_exception import (
    OnlyQuizCreatorCanSendInvitationException,
)
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.views.send_invitation_view import SendInvitationView
from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException


class TestSendInvitationView(unittest.TestCase):
    def setUp(self):
        self.quiz_id = "12345678-1234-5678-9abc-123456789abc"
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participant_id = UUID("11111111-2222-3333-4444-555555555555")
        self.invitation_id = "invitation-123"
        self.participant_email = "participant@example.com"

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id
        self.mock_user.email = "creator@example.com"

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user
        self.mock_request.data = {"participant_email": self.participant_email}

        self.mock_command_handler = Mock()
        self.mock_schema = Mock()
        self.mock_logger = Mock()
        self.view = SendInvitationView(
            command_handler=self.mock_command_handler, schema=self.mock_schema, logger=self.mock_logger
        )

    def test_post_success(self):
        mock_response = SendInvitationResponse(
            invitation_id=self.invitation_id,
            quiz_title="JavaScript Fundamentals",
            participant_email=self.participant_email,
            invited_at=datetime(2024, 1, 15, 10, 30, 0),
            invitation_acceptance_link="https://example.com/accept/invitation-123",
        )

        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["invitation_id"], self.invitation_id)
        self.assertEqual(response.data["quiz_title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["participant_email"], self.participant_email)
        self.assertIsNotNone(response.data.get("invitation_acceptance_link"))

        self.mock_command_handler.handle.assert_called_once()
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.quiz_id, self.quiz_id)
        self.assertEqual(command_arg.participant_email, self.participant_email)
        self.assertEqual(command_arg.inviter_id, str(self.user_id))
        self.assertEqual(command_arg.inviter_email, "creator@example.com")

    def test_post_handles_validation_error(self):
        self.mock_schema.side_effect = MultipleInvalid("Invalid email format")

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The request body is invalid", response.data["message"])

    def test_post_handles_quiz_not_found_exception(self):
        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.side_effect = QuizNotFoundException(self.quiz_id)

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_user_not_found_exception(self):
        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.side_effect = UserNotFoundException(self.participant_email)

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_only_quiz_creator_can_send_invitation_exception(self):
        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.side_effect = OnlyQuizCreatorCanSendInvitationException(
            quiz_id=UUID(self.quiz_id), user_id=self.user_id
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["message"],
            "User 87654321-4321-8765-cba9-987654321098 is not authorized to send invitation for quiz 12345678-1234-5678-9abc-123456789abc because it's not the creator",
        )

    def test_post_handles_invitation_already_exists_exception(self):
        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.side_effect = InvitationAlreadyExistsException(
            quiz_id=self.quiz_id, participant_id=str(self.participant_id)
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["message"],
            "Invitation already exists for participant '11111111-2222-3333-4444-555555555555' in quiz '12345678-1234-5678-9abc-123456789abc'",
        )

    def test_post_handles_unexpected_exception(self):
        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when sending invitation")

    def test_post_with_different_quiz_id(self):
        different_quiz_id = "99999999-8888-7777-6666-555555555555"
        mock_response = SendInvitationResponse(
            invitation_id="different-invitation",
            quiz_title="Python Advanced",
            participant_email=self.participant_email,
            invited_at=datetime(2024, 1, 20, 14, 0, 0),
            invitation_acceptance_link="https://example.com/accept/different-invitation",
        )

        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, different_quiz_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quiz_title"], "Python Advanced")

        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.quiz_id, different_quiz_id)

    def test_post_with_different_participant_email(self):
        different_email = "different@example.com"
        self.mock_request.data = {"participant_email": different_email}

        mock_response = SendInvitationResponse(
            invitation_id=self.invitation_id,
            quiz_title="JavaScript Fundamentals",
            participant_email=different_email,
            invited_at=datetime(2024, 1, 15, 10, 30, 0),
            invitation_acceptance_link="https://example.com/accept/invitation-123",
        )

        self.mock_schema.return_value = {"participant_email": different_email}
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["participant_email"], different_email)

        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.participant_email, different_email)

    def test_post_with_different_inviter(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id
        different_user.email = "different_creator@example.com"

        different_request = Mock()
        different_request.user = different_user
        different_request.data = {"participant_email": self.participant_email}

        mock_response = SendInvitationResponse(
            invitation_id=self.invitation_id,
            quiz_title="Django Basics",
            participant_email=self.participant_email,
            invited_at=datetime(2024, 1, 15, 10, 30, 0),
            invitation_acceptance_link="https://example.com/accept/invitation-123",
        )

        self.mock_schema.return_value = {"participant_email": self.participant_email}
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(different_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.inviter_id, str(different_user_id))
        self.assertEqual(command_arg.inviter_email, "different_creator@example.com")
