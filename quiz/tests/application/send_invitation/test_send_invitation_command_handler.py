import unittest
from unittest.mock import Mock, patch
from uuid import UUID
from datetime import datetime

from quiz.application.send_invitation.send_invitation_command import SendInvitationCommand
from quiz.application.send_invitation.send_invitation_command_handler import SendInvitationCommandHandler
from quiz.application.send_invitation.send_invitation_response import SendInvitationResponse
from quiz.domain.invitation.creator_cannot_be_invited_exception import CreatorCannotBeInvitedException
from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_repository import InvitationRepository
from quiz.domain.invitation.invitation_sender import InvitationSender
from quiz.domain.invitation.only_quiz_creator_can_send_invitation_exception import (
    OnlyQuizCreatorCanSendInvitationException,
)
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.quiz_repository import QuizRepository
from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException
from user.domain.user_repository import UserRepository


class TestSendInvitationCommandHandler(unittest.TestCase):
    def setUp(self):
        self.quiz_repository_mock = Mock(spec=QuizRepository)
        self.invitation_repository_mock = Mock(spec=InvitationRepository)
        self.user_repository_mock = Mock(spec=UserRepository)
        self.invitation_sender_mock = Mock(spec=InvitationSender)

        self.handler = SendInvitationCommandHandler(
            quiz_repository=self.quiz_repository_mock,
            invitation_repository=self.invitation_repository_mock,
            user_repository=self.user_repository_mock,
            invitation_sender=self.invitation_sender_mock,
        )

        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.inviter_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participant_id = UUID("11111111-2222-3333-4444-555555555555")
        self.invitation_id = UUID("99999999-8888-7777-6666-555555555555")

        self.command = SendInvitationCommand(
            quiz_id=str(self.quiz_id),
            inviter_id=str(self.inviter_id),
            inviter_email="creator@example.com",
            participant_email="participant@example.com",
        )

    @patch("quiz.application.send_invitation.send_invitation_command_handler.settings")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.transaction")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.uuid7")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.Invitation")
    def test_handle_success(self, mock_invitation_class, mock_uuid7, mock_transaction, mock_settings):
        mock_settings.BASE_URL = "https://example.com"

        mock_creator = Mock(spec=User)
        mock_creator.id = self.inviter_id

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "JavaScript Fundamentals"
        mock_quiz.creator = mock_creator

        mock_participant = Mock(spec=User)
        mock_participant.id = self.participant_id
        mock_participant.email = "participant@example.com"

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id
        mock_invitation.invited_at = datetime(2024, 1, 15, 10, 30, 0)

        mock_uuid7.return_value = self.invitation_id
        mock_invitation_class.return_value = mock_invitation
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.user_repository_mock.find_or_fail_by_email.return_value = mock_participant

        result = self.handler.handle(self.command)

        self.assertIsInstance(result, SendInvitationResponse)
        self.assertEqual(result.invitation_id, str(self.invitation_id))
        self.assertEqual(result.quiz_title, "JavaScript Fundamentals")
        self.assertEqual(result.participant_email, "participant@example.com")
        self.assertEqual(result.invited_at, datetime(2024, 1, 15, 10, 30, 0))
        self.assertEqual(
            result.invitation_acceptance_link, f"https://example.com/invitations/{self.invitation_id}/accept"
        )

        self.quiz_repository_mock.find_or_fail_by_id.assert_called_once_with("12345678-1234-5678-9abc-123456789abc")
        self.user_repository_mock.find_or_fail_by_email.assert_called_once_with("participant@example.com")
        mock_invitation_class.assert_called_once_with(
            id=self.invitation_id, quiz=mock_quiz, invited=mock_participant, inviter_id=str(self.inviter_id)
        )
        self.invitation_repository_mock.save.assert_called_once_with(mock_invitation)
        self.invitation_sender_mock.send_invitation_email.assert_called_once_with(
            invitation_id=self.invitation_id,
            invitation_acceptance_link=f"https://example.com/invitations/{self.invitation_id}/accept",
        )

    def test_handle_creator_cannot_be_invited_raises_exception(self):
        command_with_same_email = SendInvitationCommand(
            quiz_id=str(self.quiz_id),
            inviter_id=str(self.inviter_id),
            inviter_email="same@example.com",
            participant_email="same@example.com",
        )

        with self.assertRaises(CreatorCannotBeInvitedException) as context:
            self.handler.handle(command_with_same_email)

        self.assertEqual(context.exception.quiz_id, "12345678-1234-5678-9abc-123456789abc")
        self.assertEqual(context.exception.creator, "87654321-4321-8765-cba9-987654321098")

        self.quiz_repository_mock.find_or_fail_by_id.assert_not_called()
        self.invitation_repository_mock.save.assert_not_called()

    @patch("quiz.application.send_invitation.send_invitation_command_handler.transaction")
    def test_handle_quiz_not_found_raises_exception(self, mock_transaction):
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.side_effect = QuizNotFoundException(
            "12345678-1234-5678-9abc-123456789abc"
        )

        with self.assertRaises(QuizNotFoundException):
            self.handler.handle(self.command)

        self.user_repository_mock.find_or_fail_by_email.assert_not_called()
        self.invitation_repository_mock.save.assert_not_called()

    @patch("quiz.application.send_invitation.send_invitation_command_handler.transaction")
    def test_handle_unauthorized_inviter_raises_exception(self, mock_transaction):
        different_creator_id = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
        mock_creator = Mock(spec=User)
        mock_creator.id = different_creator_id

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.creator = mock_creator

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz

        with self.assertRaises(OnlyQuizCreatorCanSendInvitationException) as context:
            self.handler.handle(self.command)

        self.assertEqual(context.exception.quiz_id, UUID("12345678-1234-5678-9abc-123456789abc"))
        self.assertEqual(context.exception.user_id, "87654321-4321-8765-cba9-987654321098")

        self.user_repository_mock.find_or_fail_by_email.assert_not_called()
        self.invitation_repository_mock.save.assert_not_called()
        self.invitation_sender_mock.send_invitation_email.assert_not_called()

    @patch("quiz.application.send_invitation.send_invitation_command_handler.transaction")
    def test_handle_participant_not_found_raises_exception(self, mock_transaction):
        mock_creator = Mock(spec=User)
        mock_creator.id = self.inviter_id

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.creator = mock_creator

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.user_repository_mock.find_or_fail_by_email.side_effect = UserNotFoundException("participant@example.com")

        with self.assertRaises(UserNotFoundException):
            self.handler.handle(self.command)

        self.invitation_repository_mock.save.assert_not_called()
        self.invitation_sender_mock.send_invitation_email.assert_not_called()

    @patch("quiz.application.send_invitation.send_invitation_command_handler.settings")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.transaction")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.uuid7")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.Invitation")
    def test_handle_localhost_base_url(self, mock_invitation_class, mock_uuid7, mock_transaction, mock_settings):
        mock_settings.BASE_URL = "http://localhost:8000"

        mock_creator = Mock(spec=User)
        mock_creator.id = self.inviter_id

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Local Quiz"
        mock_quiz.creator = mock_creator

        mock_participant = Mock(spec=User)
        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id
        mock_invitation.invited_at = datetime.now()

        mock_uuid7.return_value = self.invitation_id
        mock_invitation_class.return_value = mock_invitation
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.user_repository_mock.find_or_fail_by_email.return_value = mock_participant

        result = self.handler.handle(self.command)

        self.assertEqual(
            result.invitation_acceptance_link, f"http://localhost:8000/invitations/{self.invitation_id}/accept"
        )
        self.invitation_sender_mock.send_invitation_email.assert_called_once_with(
            invitation_id=self.invitation_id,
            invitation_acceptance_link=f"http://localhost:8000/invitations/{self.invitation_id}/accept",
        )

    @patch("quiz.application.send_invitation.send_invitation_command_handler.settings")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.transaction")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.uuid7")
    @patch("quiz.application.send_invitation.send_invitation_command_handler.Invitation")
    def test_handle_different_emails(self, mock_invitation_class, mock_uuid7, mock_transaction, mock_settings):
        different_command = SendInvitationCommand(
            quiz_id=str(self.quiz_id),
            inviter_id=str(self.inviter_id),
            inviter_email="teacher@school.edu",
            participant_email="student@school.edu",
        )

        mock_settings.BASE_URL = "https://school.edu"

        mock_creator = Mock(spec=User)
        mock_creator.id = self.inviter_id

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.creator = mock_creator
        mock_quiz.title = "School Quiz"

        mock_participant = Mock(spec=User)
        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id
        mock_invitation.invited_at = datetime.now()

        mock_uuid7.return_value = self.invitation_id
        mock_invitation_class.return_value = mock_invitation
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.user_repository_mock.find_or_fail_by_email.return_value = mock_participant

        result = self.handler.handle(different_command)

        self.assertEqual(result.participant_email, "student@school.edu")
        self.user_repository_mock.find_or_fail_by_email.assert_called_once_with("student@school.edu")
