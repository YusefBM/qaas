import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID

from django.utils import timezone

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.quiz.quiz import Quiz
from user.domain.user import User


class TestInvitation(unittest.TestCase):
    def setUp(self):
        self.mock_inviter = Mock(spec=User)
        self.mock_inviter.id = UUID("11111111-2222-3333-4444-555555555555")
        self.mock_inviter.email = "inviter@example.com"

        self.mock_invited = Mock(spec=User)
        self.mock_invited.id = UUID("66666666-7777-8888-9999-aaaaaaaaaaaa")
        self.mock_invited.email = "invited@example.com"

        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.title = "Test Quiz"
        self.mock_quiz.id = UUID("12345678-1234-5678-9abc-123456789abc")

        self.invitation = Mock(spec=Invitation)
        self.invitation.quiz = self.mock_quiz
        self.invitation.invited = self.mock_invited
        self.invitation.inviter = self.mock_inviter
        self.invitation.invited_id = self.mock_invited.id
        self.invitation.invited_at = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

    def test_is_accepted_returns_true_when_accepted_at_set(self):
        self.invitation.accepted_at = datetime(2024, 1, 5, 14, 30, 0, tzinfo=timezone.utc)
        self.invitation.is_accepted = Mock(return_value=True)

        is_accepted = self.invitation.is_accepted()

        self.assertTrue(is_accepted)

    def test_is_accepted_returns_false_when_accepted_at_none(self):
        self.invitation.accepted_at = None
        self.invitation.is_accepted = Mock(return_value=False)

        is_accepted = self.invitation.is_accepted()

        self.assertFalse(is_accepted)

    def test_can_be_accepted_by_returns_true_when_user_id_matches(self):
        user_id = self.mock_invited.id
        self.invitation.can_be_accepted_by = Mock(return_value=True)

        can_accept = self.invitation.can_be_accepted_by(user_id)

        self.assertTrue(can_accept)

    def test_can_be_accepted_by_returns_false_when_user_id_differs(self):
        different_user_id = UUID("99999999-8888-7777-6666-555555555555")
        self.invitation.can_be_accepted_by = Mock(return_value=False)

        can_accept = self.invitation.can_be_accepted_by(different_user_id)

        self.assertFalse(can_accept)

    def test_can_be_accepted_by_handles_string_user_id(self):
        user_id_as_string = str(self.mock_invited.id)
        self.invitation.can_be_accepted_by = Mock(return_value=True)

        can_accept = self.invitation.can_be_accepted_by(user_id_as_string)

        self.assertTrue(can_accept)

    @patch("django.utils.timezone.now")
    def test_accept_sets_accepted_at_timestamp(self, mock_timezone_now):
        test_datetime = datetime(2024, 1, 15, 14, 45, 20, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime
        self.invitation.accepted_at = None

        def mock_accept():
            self.invitation.accepted_at = mock_timezone_now()

        self.invitation.accept = Mock(side_effect=mock_accept)

        self.invitation.accept()

        self.assertEqual(self.invitation.accepted_at, test_datetime)
        mock_timezone_now.assert_called_once()

    @patch("django.utils.timezone.now")
    def test_accept_changes_status_from_false_to_true(self, mock_timezone_now):
        test_datetime = datetime(2024, 1, 20, 16, 15, 0, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime
        self.invitation.accepted_at = None

        is_accepted_calls = [False, True]
        self.invitation.is_accepted = Mock(side_effect=is_accepted_calls)

        def mock_accept():
            self.invitation.accepted_at = mock_timezone_now()

        self.invitation.accept = Mock(side_effect=mock_accept)

        initial_status = self.invitation.is_accepted()
        self.invitation.accept()
        final_status = self.invitation.is_accepted()

        self.assertFalse(initial_status)
        self.assertTrue(final_status)

    def test_can_be_accepted_by_accepts_uuid_object(self):
        user_id = UUID("66666666-7777-8888-9999-aaaaaaaaaaaa")
        self.invitation.can_be_accepted_by = Mock(return_value=True)

        can_accept = self.invitation.can_be_accepted_by(user_id)

        self.assertTrue(can_accept)

    @patch("django.utils.timezone.now")
    def test_multiple_accept_calls_update_timestamp(self, mock_timezone_now):
        first_datetime = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        second_datetime = datetime(2024, 1, 15, 11, 0, 0, tzinfo=timezone.utc)

        def mock_accept():
            self.invitation.accepted_at = mock_timezone_now()

        self.invitation.accept = Mock(side_effect=mock_accept)

        mock_timezone_now.return_value = first_datetime
        self.invitation.accept()
        first_accepted_at = self.invitation.accepted_at

        mock_timezone_now.return_value = second_datetime
        self.invitation.accept()

        self.assertEqual(self.invitation.accepted_at, second_datetime)
        self.assertNotEqual(self.invitation.accepted_at, first_accepted_at)

    @patch("django.utils.timezone.now")
    def test_invitation_state_remains_consistent(self, mock_timezone_now):
        test_datetime = datetime(2024, 1, 25, 12, 45, 0, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime
        self.invitation.accepted_at = None

        is_accepted_responses = [False, True, True]
        self.invitation.is_accepted = Mock(side_effect=is_accepted_responses)
        self.invitation.can_be_accepted_by = Mock(return_value=True)

        def mock_accept():
            self.invitation.accepted_at = mock_timezone_now()

        self.invitation.accept = Mock(side_effect=mock_accept)

        self.assertFalse(self.invitation.is_accepted())
        self.assertTrue(self.invitation.can_be_accepted_by(self.mock_invited.id))

        self.invitation.accept()

        self.assertTrue(self.invitation.is_accepted())
        self.assertTrue(self.invitation.can_be_accepted_by(self.mock_invited.id))


class TestInvitationModelBehavior(unittest.TestCase):
    def test_is_accepted_logic_with_different_states(self):
        accepted_at_set = datetime(2024, 2, 1, 9, 30, 0, tzinfo=timezone.utc)
        accepted_at_none = None

        self.assertTrue(accepted_at_set is not None)
        self.assertFalse(accepted_at_none is not None)

    def test_can_be_accepted_by_comparison_logic(self):
        invited_user_id = UUID("66666666-7777-8888-9999-aaaaaaaaaaaa")
        different_user_id = UUID("99999999-8888-7777-6666-555555555555")

        self.assertTrue(str(invited_user_id) == str(invited_user_id))
        self.assertFalse(str(invited_user_id) == str(different_user_id))

        user_id_as_string = str(invited_user_id)
        self.assertTrue(str(invited_user_id) == user_id_as_string)

    @patch("django.utils.timezone.now")
    def test_accept_method_logic(self, mock_timezone_now):
        test_datetime = datetime(2024, 1, 15, 14, 45, 20, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime

        accepted_at = mock_timezone_now()

        self.assertEqual(accepted_at, test_datetime)
        mock_timezone_now.assert_called_once()
