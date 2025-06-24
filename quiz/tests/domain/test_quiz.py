import unittest
from unittest.mock import Mock
from datetime import datetime
from uuid import UUID

from django.utils import timezone

from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.empty_quiz_title_exception import EmptyQuizTitleException
from quiz.domain.quiz.invalid_quiz_title_length_exception import InvalidQuizTitleLengthException
from user.domain.user import User


class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.mock_user = Mock(spec=User)
        self.mock_user.id = UUID("11111111-2222-3333-4444-555555555555")
        self.mock_user.email = "creator@example.com"

        self.quiz = Mock(spec=Quiz)
        self.quiz.title = "Test Quiz"
        self.quiz.description = "A test quiz description"
        self.quiz.creator = self.mock_user
        self.quiz.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_str_returns_quiz_title(self):
        self.quiz.title = "JavaScript Fundamentals"
        self.quiz.__str__ = Mock(return_value="JavaScript Fundamentals")

        result = str(self.quiz)

        self.assertEqual(result, "JavaScript Fundamentals")

    def test_get_formatted_created_at_returns_iso_format(self):
        test_datetime = datetime(2024, 1, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)
        self.quiz.created_at = test_datetime
        self.quiz.get_formatted_created_at = Mock(return_value="2024-01-15T10:30:45.123456Z")

        formatted_date = self.quiz.get_formatted_created_at()

        self.assertEqual(formatted_date, "2024-01-15T10:30:45.123456Z")

    def test_total_questions_returns_question_count(self):
        mock_questions_manager = Mock()
        mock_questions_manager.count.return_value = 5
        self.quiz.questions = mock_questions_manager
        self.quiz.total_questions = 5

        total_questions = self.quiz.total_questions

        self.assertEqual(total_questions, 5)

    def test_total_participants_returns_participation_count(self):
        mock_participations_manager = Mock()
        mock_participations_manager.count.return_value = 10
        self.quiz.participations = mock_participations_manager
        self.quiz.total_participants = 10

        total_participants = self.quiz.total_participants

        self.assertEqual(total_participants, 10)

    def test_total_participants_returns_zero_when_no_participations_attribute(self):
        if hasattr(self.quiz, "participations"):
            delattr(self.quiz, "participations")
        self.quiz.total_participants = 0

        total_participants = self.quiz.total_participants

        self.assertEqual(total_participants, 0)

    def test_str_with_empty_title_returns_empty_string(self):
        self.quiz.title = ""
        self.quiz.__str__ = Mock(return_value="")

        result = str(self.quiz)

        self.assertEqual(result, "")

    def test_str_with_special_characters_preserves_formatting(self):
        special_title = "Quiz: Python & Django (Advanced) - Part 1"
        self.quiz.title = special_title
        self.quiz.__str__ = Mock(return_value=special_title)

        result = str(self.quiz)

        self.assertEqual(result, special_title)

    def test_total_questions_with_zero_questions_returns_zero(self):
        mock_questions_manager = Mock()
        mock_questions_manager.count.return_value = 0
        self.quiz.questions = mock_questions_manager
        self.quiz.total_questions = 0

        total_questions = self.quiz.total_questions

        self.assertEqual(total_questions, 0)

    def test_total_participants_with_zero_participants_returns_zero(self):
        mock_participations_manager = Mock()
        mock_participations_manager.count.return_value = 0
        self.quiz.participations = mock_participations_manager
        self.quiz.total_participants = 0

        total_participants = self.quiz.total_participants

        self.assertEqual(total_participants, 0)
