import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from django.db import IntegrityError

from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.answer_already_exists_exception import AnswerAlreadyExistsException
from quiz.infrastructure.db_answer_repository import DbAnswerRepository


class TestDbAnswerRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbAnswerRepository()
        self.answer_id = 1
        self.question_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.answer_order = 1

    def test_save_success(self):
        answer = Mock(spec=Answer)
        answer.id = self.answer_id
        answer.text = "JavaScript"
        answer.order = self.answer_order
        answer.question_id = self.question_id

        self.repository.save(answer)

        answer.save.assert_called_once()

    def test_save_raises_answer_already_exists_exception_on_unique_constraint_violation(self):
        answer = Mock(spec=Answer)
        answer.order = self.answer_order
        answer.question_id = self.question_id

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_answer_question_id_order"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        answer.save.side_effect = integrity_error

        with self.assertRaises(AnswerAlreadyExistsException) as context:
            self.repository.save(answer)

        self.assertEqual(context.exception.order, self.answer_order)
        self.assertEqual(context.exception.question_id, self.question_id)

    def test_save_raises_original_integrity_error_on_other_constraint_violation(self):
        answer = Mock(spec=Answer)

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "some_other_constraint"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Other database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        answer.save.side_effect = integrity_error

        with self.assertRaises(IntegrityError):
            self.repository.save(answer)

    @patch("quiz.domain.quiz.answer.Answer.objects")
    def test_find_by_id_success(self, mock_objects):
        expected_answer = Mock(spec=Answer)
        expected_answer.id = self.answer_id
        expected_answer.text = "Python"

        mock_objects.get.return_value = expected_answer

        result = self.repository.find_by_id(self.answer_id)

        self.assertEqual(result, expected_answer)
        mock_objects.get.assert_called_once_with(id=self.answer_id)

    @patch("quiz.domain.quiz.answer.Answer.objects")
    def test_find_by_id_returns_none_when_not_found(self, mock_objects):
        mock_objects.get.side_effect = Answer.DoesNotExist

        result = self.repository.find_by_id(self.answer_id)

        self.assertIsNone(result)

    @patch("quiz.domain.quiz.answer.Answer.objects")
    def test_find_by_ids_success_with_multiple_answers(self, mock_objects):
        answer1 = Mock(spec=Answer)
        answer1.id = 1
        answer1.text = "Answer 1"

        answer2 = Mock(spec=Answer)
        answer2.id = 2
        answer2.text = "Answer 2"

        answer3 = Mock(spec=Answer)
        answer3.id = 3
        answer3.text = "Answer 3"

        mock_objects.filter.return_value = [answer1, answer2, answer3]
        answer_ids = [1, 2, 3]

        result = self.repository.find_by_ids(answer_ids)

        expected_result = {1: answer1, 2: answer2, 3: answer3}
        self.assertEqual(result, expected_result)
        mock_objects.filter.assert_called_once_with(id__in=answer_ids)

    @patch("quiz.domain.quiz.answer.Answer.objects")
    def test_find_by_ids_success_with_single_answer(self, mock_objects):
        answer = Mock(spec=Answer)
        answer.id = 1
        answer.text = "Single Answer"

        mock_objects.filter.return_value = [answer]
        answer_ids = [1]

        result = self.repository.find_by_ids(answer_ids)

        expected_result = {1: answer}
        self.assertEqual(result, expected_result)

    @patch("quiz.domain.quiz.answer.Answer.objects")
    def test_find_by_ids_returns_empty_dict_when_no_answers_found(self, mock_objects):
        mock_objects.filter.return_value = []
        answer_ids = [1, 2, 3]

        result = self.repository.find_by_ids(answer_ids)

        self.assertEqual(result, {})

    @patch("quiz.domain.quiz.answer.Answer.objects")
    def test_find_by_ids_with_empty_list(self, mock_objects):
        mock_objects.filter.return_value = []
        answer_ids = []

        result = self.repository.find_by_ids(answer_ids)

        self.assertEqual(result, {})
        mock_objects.filter.assert_called_once_with(id__in=[])

    @patch.object(DbAnswerRepository, "save")
    def test_bulk_save_success_with_multiple_answers(self, mock_save):
        answer1 = Mock(spec=Answer)
        answer1.id = 1

        answer2 = Mock(spec=Answer)
        answer2.id = 2

        answer3 = Mock(spec=Answer)
        answer3.id = 3

        answers = [answer1, answer2, answer3]

        self.repository.bulk_save(answers)

        self.assertEqual(mock_save.call_count, 3)
        mock_save.assert_any_call(answer1)
        mock_save.assert_any_call(answer2)
        mock_save.assert_any_call(answer3)

    @patch.object(DbAnswerRepository, "save")
    def test_bulk_save_success_with_single_answer(self, mock_save):
        answer = Mock(spec=Answer)
        answer.id = 1

        answers = [answer]

        self.repository.bulk_save(answers)

        mock_save.assert_called_once_with(answer)

    @patch.object(DbAnswerRepository, "save")
    def test_bulk_save_with_empty_list(self, mock_save):
        answers = []

        self.repository.bulk_save(answers)

        mock_save.assert_not_called()

    @patch.object(DbAnswerRepository, "save")
    def test_bulk_save_propagates_exception_from_save(self, mock_save):
        answer = Mock(spec=Answer)
        answer.order = self.answer_order
        answer.question_id = self.question_id

        mock_save.side_effect = AnswerAlreadyExistsException(order=self.answer_order, question_id=self.question_id)
        answers = [answer]

        with self.assertRaises(AnswerAlreadyExistsException):
            self.repository.bulk_save(answers)
