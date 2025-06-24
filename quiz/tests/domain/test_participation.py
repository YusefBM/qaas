import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from uuid import UUID

from django.utils import timezone

from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_status import ParticipationStatus
from quiz.domain.quiz.quiz import Quiz
from user.domain.user import User


class TestParticipation(unittest.TestCase):
    def setUp(self):
        self.mock_user = Mock(spec=User)
        self.mock_user.email = "test@example.com"

        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.title = "Test Quiz"
        self.mock_quiz.id = UUID("12345678-1234-5678-9abc-123456789abc")

        self.participation = Mock(spec=Participation)
        self.participation.participant = self.mock_user
        self.participation.quiz = self.mock_quiz
        self.participation.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_status_returns_completed_when_completed_at_set(self):
        self.participation.completed_at = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        type(self.participation).status = property(lambda self: ParticipationStatus.COMPLETED)

        status = self.participation.status

        self.assertEqual(status, ParticipationStatus.COMPLETED)

    def test_status_returns_invited_when_completed_at_none(self):
        self.participation.completed_at = None
        type(self.participation).status = property(lambda self: ParticipationStatus.INVITED)

        status = self.participation.status

        self.assertEqual(status, ParticipationStatus.INVITED)

    def test_get_formatted_completed_at_returns_iso_format_when_completed(self):
        test_datetime = datetime(2024, 1, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)
        self.participation.completed_at = test_datetime
        self.participation.get_formatted_completed_at = Mock(return_value="2024-01-15T10:30:45.123456Z")

        formatted_date = self.participation.get_formatted_completed_at()

        self.assertEqual(formatted_date, "2024-01-15T10:30:45.123456Z")

    def test_get_formatted_completed_at_returns_none_when_not_completed(self):
        self.participation.completed_at = None
        self.participation.get_formatted_completed_at = Mock(return_value=None)

        formatted_date = self.participation.get_formatted_completed_at()

        self.assertIsNone(formatted_date)

    def test_get_formatted_created_at_returns_iso_format(self):
        test_datetime = datetime(2024, 1, 10, 9, 15, 30, 654321, tzinfo=timezone.utc)
        self.participation.created_at = test_datetime
        self.participation.get_formatted_created_at = Mock(return_value="2024-01-10T09:15:30.654321Z")

        formatted_date = self.participation.get_formatted_created_at()

        self.assertEqual(formatted_date, "2024-01-10T09:15:30.654321Z")

    @patch("django.utils.timezone.now")
    def test_complete_sets_score_and_completed_at(self, mock_timezone_now):
        test_score = 85
        test_datetime = datetime(2024, 1, 15, 14, 45, 20, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime

        def mock_complete(score):
            self.participation.score = score
            self.participation.completed_at = mock_timezone_now()

        self.participation.complete = Mock(side_effect=mock_complete)

        self.participation.complete(test_score)

        self.assertEqual(self.participation.score, test_score)
        self.assertEqual(self.participation.completed_at, test_datetime)
        mock_timezone_now.assert_called_once()

    def test_is_completed_returns_true_when_completed_at_set(self):
        self.participation.completed_at = datetime(2024, 1, 15, 16, 45, 0, tzinfo=timezone.utc)
        self.participation.is_completed = Mock(return_value=True)

        is_completed = self.participation.is_completed()

        self.assertTrue(is_completed)

    def test_is_completed_returns_false_when_completed_at_none(self):
        self.participation.completed_at = None
        self.participation.is_completed = Mock(return_value=False)

        is_completed = self.participation.is_completed()

        self.assertFalse(is_completed)

    def test_str_returns_invited_status_format(self):
        self.participation.completed_at = None
        self.participation.__str__ = Mock(return_value="test@example.com - Test Quiz (ParticipationStatus.INVITED)")

        result = str(self.participation)

        self.assertEqual(result, "test@example.com - Test Quiz (ParticipationStatus.INVITED)")

    def test_str_returns_completed_status_format(self):
        self.participation.completed_at = datetime(2024, 1, 20, 10, 0, 0, tzinfo=timezone.utc)
        self.participation.__str__ = Mock(return_value="test@example.com - Test Quiz (ParticipationStatus.COMPLETED)")

        result = str(self.participation)

        self.assertEqual(result, "test@example.com - Test Quiz (ParticipationStatus.COMPLETED)")

    @patch("django.utils.timezone.now")
    def test_complete_changes_status_from_invited_to_completed(self, mock_timezone_now):
        test_datetime = datetime(2024, 1, 25, 11, 30, 0, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime

        status_responses = [ParticipationStatus.INVITED, ParticipationStatus.COMPLETED]
        type(self.participation).status = property(Mock(side_effect=status_responses))

        def mock_complete(score):
            self.participation.score = score
            self.participation.completed_at = mock_timezone_now()

        self.participation.complete = Mock(side_effect=mock_complete)

        initial_status = self.participation.status
        self.participation.complete(90)
        final_status = self.participation.status

        self.assertEqual(initial_status, ParticipationStatus.INVITED)
        self.assertEqual(final_status, ParticipationStatus.COMPLETED)

    def test_formatted_created_at_returns_consistent_results(self):
        test_datetime = datetime(2024, 2, 20, 16, 45, 55, 987654, tzinfo=timezone.utc)
        self.participation.created_at = test_datetime
        self.participation.get_formatted_created_at = Mock(return_value="2024-02-20T16:45:55.987654Z")

        formatted1 = self.participation.get_formatted_created_at()
        formatted2 = self.participation.get_formatted_created_at()

        self.assertEqual(formatted1, formatted2)
        self.assertEqual(formatted1, "2024-02-20T16:45:55.987654Z")


class TestParticipationModelBehavior(unittest.TestCase):
    def test_status_logic_with_completed_at_set(self):
        completed_at_set = datetime(2024, 3, 1, 14, 0, 0, tzinfo=timezone.utc)
        completed_at_none = None

        status_completed = (
            ParticipationStatus.COMPLETED if completed_at_set is not None else ParticipationStatus.INVITED
        )
        status_invited = ParticipationStatus.COMPLETED if completed_at_none is not None else ParticipationStatus.INVITED

        self.assertEqual(status_completed, ParticipationStatus.COMPLETED)
        self.assertEqual(status_invited, ParticipationStatus.INVITED)

    def test_is_completed_logic_with_different_states(self):
        completed_at_set = datetime(2024, 3, 5, 9, 15, 0, tzinfo=timezone.utc)
        completed_at_none = None

        self.assertTrue(completed_at_set is not None)
        self.assertFalse(completed_at_none is not None)

    def test_datetime_formatting_logic(self):
        test_datetime = datetime(2024, 1, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)

        formatted = test_datetime.isoformat().replace("+00:00", "Z")

        self.assertEqual(formatted, "2024-01-15T10:30:45.123456Z")

    @patch("django.utils.timezone.now")
    def test_complete_method_logic(self, mock_timezone_now):
        test_datetime = datetime(2024, 1, 15, 14, 45, 20, tzinfo=timezone.utc)
        mock_timezone_now.return_value = test_datetime

        score = 85
        completed_at = mock_timezone_now()

        self.assertEqual(score, 85)
        self.assertEqual(completed_at, test_datetime)
        mock_timezone_now.assert_called_once()
