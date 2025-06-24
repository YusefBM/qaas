import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.application.accept_invitation.accept_invitation_command import AcceptInvitationCommand
from quiz.application.accept_invitation.accept_invitation_command_handler import AcceptInvitationCommandHandler
from quiz.application.accept_invitation.accept_invitation_response import AcceptInvitationResponse
from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_already_accepted_exception import InvitationAlreadyAcceptedException
from quiz.domain.invitation.invitation_repository import InvitationRepository
from quiz.domain.invitation.only_invited_user_can_accept_invitation_exception import (
    OnlyInvitedUserCanAcceptInvitationException,
)
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.quiz.quiz import Quiz
from user.domain.user import User


class TestAcceptInvitationCommandHandler(unittest.TestCase):
    def setUp(self):
        self.invitation_repository_mock = Mock(spec=InvitationRepository)
        self.participation_repository_mock = Mock(spec=ParticipationRepository)

        self.handler = AcceptInvitationCommandHandler(
            invitation_repository=self.invitation_repository_mock,
            participation_repository=self.participation_repository_mock,
        )

        self.invitation_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.participant_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.unauthorized_user_id = UUID("11111111-1111-1111-1111-111111111111")
        self.quiz_id = UUID("11111111-2222-3333-4444-555555555555")
        self.participation_id = UUID("99999999-8888-7777-6666-555555555555")

        self.command = AcceptInvitationCommand(invitation_id=self.invitation_id, user_id=self.participant_id)

    @patch("quiz.application.accept_invitation.accept_invitation_command_handler.Participation")
    @patch("quiz.application.accept_invitation.accept_invitation_command_handler.transaction")
    @patch("quiz.application.accept_invitation.accept_invitation_command_handler.uuid7")
    def test_handle(self, mock_uuid7, mock_transaction, mock_participation_class):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "JavaScript Fundamentals Quiz"

        mock_participant = Mock(spec=User)
        mock_participant.id = self.participant_id

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id
        mock_invitation.is_accepted.return_value = False
        mock_invitation.can_be_accepted_by.return_value = True
        mock_invitation.quiz = mock_quiz
        mock_invitation.invited = mock_participant

        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation
        mock_uuid7.return_value = self.participation_id
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        mock_participation_instance = Mock(spec=Participation)
        mock_participation_instance.id = self.participation_id
        mock_participation_class.return_value = mock_participation_instance

        result = self.handler.handle(self.command)
        self.assertIsInstance(result, AcceptInvitationResponse)
        self.assertEqual(result.message, "Invitation accepted successfully")
        self.assertEqual(result.invitation_id, self.invitation_id)
        self.assertEqual(result.participation_id, self.participation_id)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "JavaScript Fundamentals Quiz")
        self.invitation_repository_mock.find_or_fail_by_id.assert_called_once_with(self.invitation_id)
        mock_invitation.can_be_accepted_by.assert_called_once_with(self.participant_id)
        mock_invitation.is_accepted.assert_called_once()
        mock_invitation.accept.assert_called_once()
        self.invitation_repository_mock.save.assert_called_once_with(mock_invitation)
        mock_participation_class.assert_called_once_with(
            id=self.participation_id, quiz=mock_quiz, participant=mock_participant, invitation=mock_invitation
        )
        self.participation_repository_mock.save.assert_called_once_with(mock_participation_instance)
        mock_uuid7.assert_called_once()

    def test_handle_invitation_already_accepted_raises_exception(self):
        mock_invitation = Mock(spec=Invitation)
        mock_invitation.is_accepted.return_value = True
        mock_invitation.can_be_accepted_by.return_value = True
        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        with self.assertRaises(InvitationAlreadyAcceptedException) as context:
            self.handler.handle(self.command)

        self.assertEqual(context.exception.invitation_id, UUID("12345678-1234-5678-9abc-123456789abc"))
        mock_invitation.accept.assert_not_called()
        self.invitation_repository_mock.save.assert_not_called()
        self.participation_repository_mock.save.assert_not_called()

    def test_handle_unauthorized_user_raises_exception(self):
        unauthorized_command = AcceptInvitationCommand(
            invitation_id=self.invitation_id, user_id=self.unauthorized_user_id
        )

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.is_accepted.return_value = False
        mock_invitation.can_be_accepted_by.return_value = False
        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        with self.assertRaises(OnlyInvitedUserCanAcceptInvitationException) as context:
            self.handler.handle(unauthorized_command)

        self.assertEqual(context.exception.invitation_id, UUID("12345678-1234-5678-9abc-123456789abc"))
        self.assertEqual(context.exception.user_id, UUID("11111111-1111-1111-1111-111111111111"))

        self.invitation_repository_mock.find_or_fail_by_id.assert_called_once_with(self.invitation_id)
        mock_invitation.can_be_accepted_by.assert_called_once_with(self.unauthorized_user_id)
        mock_invitation.is_accepted.assert_not_called()
        mock_invitation.accept.assert_not_called()
        self.invitation_repository_mock.save.assert_not_called()
        self.participation_repository_mock.save.assert_not_called()

    def test_handle_checks_authorization_before_acceptance_status(self):
        unauthorized_command = AcceptInvitationCommand(
            invitation_id=self.invitation_id, user_id=self.unauthorized_user_id
        )

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.can_be_accepted_by.return_value = False
        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        with self.assertRaises(OnlyInvitedUserCanAcceptInvitationException):
            self.handler.handle(unauthorized_command)

        mock_invitation.can_be_accepted_by.assert_called_once_with(self.unauthorized_user_id)
        mock_invitation.is_accepted.assert_not_called()
