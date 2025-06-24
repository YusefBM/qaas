import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from django.db import IntegrityError

from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_already_exists_exception import QuizAlreadyExistsException
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.db_quiz_repository import DbQuizRepository


class TestDbQuizRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbQuizRepository()
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.creator_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participant_id = UUID("11111111-2222-3333-4444-555555555555")

    def _create_mock_cause(self, constraint_name):
        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = constraint_name

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        return MockCause()

    def test_save_success(self):
        quiz = Mock(spec=Quiz)
        quiz.title = "JavaScript Basics"
        quiz.creator_id = self.creator_id

        self.repository.save(quiz)

        quiz.save.assert_called_once()

    def test_save_raises_quiz_already_exists_exception_on_unique_constraint_violation(self):
        quiz = Mock(spec=Quiz)
        quiz.title = "Python Fundamentals"
        quiz.creator_id = self.creator_id

        mock_cause = self._create_mock_cause("quiz_quiz_title_creator_id")

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        quiz.save.side_effect = integrity_error

        with self.assertRaises(QuizAlreadyExistsException) as context:
            self.repository.save(quiz)

        self.assertEqual(context.exception.title, "Python Fundamentals")
        self.assertEqual(context.exception.creator_id, self.creator_id)

    def test_save_raises_original_integrity_error_on_other_constraint_violation(self):
        quiz = Mock(spec=Quiz)

        mock_cause = self._create_mock_cause("some_other_constraint")

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        quiz.save.side_effect = integrity_error

        with self.assertRaises(IntegrityError):
            self.repository.save(quiz)

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_or_fail_by_id_success(self, mock_objects):
        expected_quiz = Mock(spec=Quiz)
        expected_quiz.id = self.quiz_id
        expected_quiz.title = "Django Advanced"

        mock_objects.get.return_value = expected_quiz

        result = self.repository.find_or_fail_by_id(self.quiz_id)

        self.assertEqual(result, expected_quiz)
        mock_objects.get.assert_called_once_with(id=self.quiz_id)

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_or_fail_by_id_raises_quiz_not_found_exception(self, mock_objects):
        mock_objects.get.side_effect = Quiz.DoesNotExist

        with self.assertRaises(QuizNotFoundException) as context:
            self.repository.find_or_fail_by_id(self.quiz_id)

        self.assertEqual(context.exception.quiz_id, str(self.quiz_id))

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_by_creator_id_returns_ordered_list(self, mock_objects):
        quiz1 = Mock(spec=Quiz)
        quiz1.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        quiz1.title = "First Quiz"

        quiz2 = Mock(spec=Quiz)
        quiz2.id = UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff")
        quiz2.title = "Second Quiz"

        mock_queryset = Mock()
        mock_queryset.order_by.return_value = [quiz1, quiz2]
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_by_creator_id(self.creator_id)

        self.assertEqual(result, [quiz1, quiz2])
        mock_objects.filter.assert_called_once_with(creator_id=self.creator_id)
        mock_queryset.order_by.assert_called_once_with("-created_at")

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_by_creator_id_returns_empty_list_when_no_quizzes(self, mock_objects):
        mock_queryset = Mock()
        mock_queryset.order_by.return_value = []
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_by_creator_id(self.creator_id)

        self.assertEqual(result, [])

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_by_participant_id_returns_distinct_ordered_list(self, mock_objects):
        quiz1 = Mock(spec=Quiz)
        quiz1.id = UUID("cccccccc-dddd-eeee-ffff-000000000000")
        quiz1.title = "Participated Quiz 1"

        quiz2 = Mock(spec=Quiz)
        quiz2.id = UUID("dddddddd-eeee-ffff-0000-111111111111")
        quiz2.title = "Participated Quiz 2"

        mock_queryset = Mock()
        mock_distinct_queryset = Mock()

        mock_queryset.distinct.return_value = mock_distinct_queryset
        mock_distinct_queryset.order_by.return_value = [quiz1, quiz2]
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_by_participant_id(self.participant_id)

        self.assertEqual(result, [quiz1, quiz2])
        mock_objects.filter.assert_called_once_with(participations__participant_id=self.participant_id)
        mock_queryset.distinct.assert_called_once()
        mock_distinct_queryset.order_by.assert_called_once_with("-created_at")

    @patch("quiz.domain.quiz.quiz.Quiz.objects")
    def test_find_by_participant_id_returns_empty_list_when_no_participations(self, mock_objects):
        mock_queryset = Mock()
        mock_distinct_queryset = Mock()

        mock_queryset.distinct.return_value = mock_distinct_queryset
        mock_distinct_queryset.order_by.return_value = []
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_by_participant_id(self.participant_id)

        self.assertEqual(result, [])

    def test_is_unique_constraint_violation_returns_true_for_title_creator_constraint(self):
        mock_cause = self._create_mock_cause("quiz_quiz_title_creator_id")

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        result = self.repository._is_unique_constraint_violation(integrity_error)

        self.assertTrue(result)

    def test_is_unique_constraint_violation_returns_false_for_other_constraints(self):
        mock_cause = self._create_mock_cause("some_other_constraint")

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        result = self.repository._is_unique_constraint_violation(integrity_error)

        self.assertFalse(result)
