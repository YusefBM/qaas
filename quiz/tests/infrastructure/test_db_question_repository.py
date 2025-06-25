import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from django.db import IntegrityError

from quiz.domain.quiz.question import Question
from quiz.domain.quiz.question_already_exists_exception import QuestionAlreadyExistsException
from quiz.infrastructure.db_question_repository import DbQuestionRepository


class TestDbQuestionRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbQuestionRepository()
        self.question_id = 1
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.question_order = 1

    def test_save_success(self):
        question = Mock(spec=Question)
        question.id = self.question_id
        question.text = "What is JavaScript?"
        question.order = self.question_order
        question.quiz_id = self.quiz_id

        self.repository.save(question)

        question.save.assert_called_once()

    def test_save_raises_question_already_exists_exception_on_unique_constraint_violation(self):
        question = Mock(spec=Question)
        question.order = self.question_order
        question.quiz_id = self.quiz_id

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_question_quiz_id_order"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        question.save.side_effect = integrity_error

        with self.assertRaises(QuestionAlreadyExistsException) as context:
            self.repository.save(question)

        self.assertEqual(context.exception.order, self.question_order)
        self.assertEqual(context.exception.quiz_id, self.quiz_id)

    def test_save_raises_original_integrity_error_on_other_constraint_violation(self):
        question = Mock(spec=Question)

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "some_other_constraint"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Other database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        question.save.side_effect = integrity_error

        with self.assertRaises(IntegrityError):
            self.repository.save(question)

    @patch("quiz.domain.quiz.question.Question.objects")
    def test_find_by_ids_success_with_multiple_questions(self, mock_objects):
        question1 = Mock(spec=Question)
        question1.id = 1
        question1.text = "Question 1"

        question2 = Mock(spec=Question)
        question2.id = 2
        question2.text = "Question 2"

        question3 = Mock(spec=Question)
        question3.id = 3
        question3.text = "Question 3"

        mock_objects.filter.return_value = [question1, question2, question3]
        question_ids = [1, 2, 3]

        result = self.repository.find_by_ids(question_ids)

        expected_result = {1: question1, 2: question2, 3: question3}
        self.assertEqual(result, expected_result)
        mock_objects.filter.assert_called_once_with(id__in=question_ids)

    @patch("quiz.domain.quiz.question.Question.objects")
    def test_find_by_ids_success_with_single_question(self, mock_objects):
        question = Mock(spec=Question)
        question.id = 1
        question.text = "Single Question"

        mock_objects.filter.return_value = [question]
        question_ids = [1]

        result = self.repository.find_by_ids(question_ids)

        expected_result = {1: question}
        self.assertEqual(result, expected_result)

    @patch("quiz.domain.quiz.question.Question.objects")
    def test_find_by_ids_returns_empty_dict_when_no_questions_found(self, mock_objects):
        mock_objects.filter.return_value = []
        question_ids = [1, 2, 3]

        result = self.repository.find_by_ids(question_ids)

        self.assertEqual(result, {})

    @patch("quiz.domain.quiz.question.Question.objects")
    def test_find_by_ids_with_empty_list(self, mock_objects):
        mock_objects.filter.return_value = []
        question_ids = []

        result = self.repository.find_by_ids(question_ids)

        self.assertEqual(result, {})
        mock_objects.filter.assert_called_once_with(id__in=[])

    @patch("quiz.domain.quiz.question.Question.objects")
    def test_find_by_ids_with_partial_results(self, mock_objects):
        question1 = Mock(spec=Question)
        question1.id = 1
        question1.text = "Found Question"

        mock_objects.filter.return_value = [question1]
        question_ids = [1, 2, 3]

        result = self.repository.find_by_ids(question_ids)

        expected_result = {1: question1}
        self.assertEqual(result, expected_result)
        self.assertEqual(len(result), 1)

    @patch("quiz.domain.quiz.question.Question.objects")
    def test_find_by_ids_maintains_question_mapping_correctly(self, mock_objects):
        question_a = Mock(spec=Question)
        question_a.id = 10
        question_a.text = "Question A"

        question_b = Mock(spec=Question)
        question_b.id = 20
        question_b.text = "Question B"

        mock_objects.filter.return_value = [question_a, question_b]
        question_ids = [10, 20]

        result = self.repository.find_by_ids(question_ids)

        self.assertEqual(result[10], question_a)
        self.assertEqual(result[20], question_b)
        self.assertEqual(len(result), 2)
