import unittest
from unittest.mock import Mock, patch

from django.db import IntegrityError

from quiz.domain.participation.answer_submission import AnswerSubmission
from quiz.domain.participation.duplicate_answer_submission_exception import DuplicateAnswerSubmissionException
from quiz.domain.quiz.question import Question
from quiz.infrastructure.db_answer_submission_repository import DbAnswerSubmissionRepository


class TestDbAnswerSubmissionRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbAnswerSubmissionRepository()
        self.question_id = 1

        self.mock_question = Mock(spec=Question)
        self.mock_question.id = self.question_id

    def test_save_success(self):
        answer_submission = Mock(spec=AnswerSubmission)
        answer_submission.question = self.mock_question
        answer_submission.selected_answer_id = 1

        self.repository.save(answer_submission)

        answer_submission.save.assert_called_once()

    def test_save_raises_duplicate_answer_submission_exception_on_unique_constraint_violation(self):
        answer_submission = Mock(spec=AnswerSubmission)
        answer_submission.question = self.mock_question

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_answersubmission_participation_id_question_id"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        answer_submission.save.side_effect = integrity_error

        with self.assertRaises(DuplicateAnswerSubmissionException) as context:
            self.repository.save(answer_submission)

        self.assertEqual(context.exception.question_id, self.question_id)

    def test_save_raises_original_integrity_error_on_other_constraint_violation(self):
        answer_submission = Mock(spec=AnswerSubmission)

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "some_other_constraint"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Other database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        answer_submission.save.side_effect = integrity_error

        with self.assertRaises(IntegrityError):
            self.repository.save(answer_submission)

    @patch.object(DbAnswerSubmissionRepository, "save")
    def test_bulk_save_success_with_multiple_submissions(self, mock_save):
        submission1 = Mock(spec=AnswerSubmission)
        submission1.question = self.mock_question

        submission2 = Mock(spec=AnswerSubmission)
        submission2.question = self.mock_question

        submission3 = Mock(spec=AnswerSubmission)
        submission3.question = self.mock_question

        submissions = [submission1, submission2, submission3]

        self.repository.bulk_save(submissions)

        self.assertEqual(mock_save.call_count, 3)
        mock_save.assert_any_call(submission1)
        mock_save.assert_any_call(submission2)
        mock_save.assert_any_call(submission3)

    @patch.object(DbAnswerSubmissionRepository, "save")
    def test_bulk_save_success_with_single_submission(self, mock_save):
        submission = Mock(spec=AnswerSubmission)
        submission.question = self.mock_question

        submissions = [submission]

        self.repository.bulk_save(submissions)

        mock_save.assert_called_once_with(submission)

    @patch.object(DbAnswerSubmissionRepository, "save")
    def test_bulk_save_with_empty_list(self, mock_save):
        submissions = []

        self.repository.bulk_save(submissions)

        mock_save.assert_not_called()

    @patch.object(DbAnswerSubmissionRepository, "save")
    def test_bulk_save_propagates_exception_from_save(self, mock_save):
        submission = Mock(spec=AnswerSubmission)
        submission.question = self.mock_question

        mock_save.side_effect = DuplicateAnswerSubmissionException(question_id=self.question_id)
        submissions = [submission]

        with self.assertRaises(DuplicateAnswerSubmissionException):
            self.repository.bulk_save(submissions)

    @patch.object(DbAnswerSubmissionRepository, "save")
    def test_bulk_save_stops_on_first_exception(self, mock_save):
        submission1 = Mock(spec=AnswerSubmission)
        submission1.question = self.mock_question

        submission2 = Mock(spec=AnswerSubmission)
        submission2.question = self.mock_question

        submission3 = Mock(spec=AnswerSubmission)
        submission3.question = self.mock_question

        mock_save.side_effect = [None, DuplicateAnswerSubmissionException(question_id=self.question_id), None]
        submissions = [submission1, submission2, submission3]

        with self.assertRaises(DuplicateAnswerSubmissionException):
            self.repository.bulk_save(submissions)

        self.assertEqual(mock_save.call_count, 2)
        mock_save.assert_any_call(submission1)
        mock_save.assert_any_call(submission2)

    def test_save_with_different_question_ids(self):
        different_question = Mock(spec=Question)
        different_question.id = 99

        answer_submission = Mock(spec=AnswerSubmission)
        answer_submission.question = different_question

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_answersubmission_participation_id_question_id"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        answer_submission.save.side_effect = integrity_error

        with self.assertRaises(DuplicateAnswerSubmissionException) as context:
            self.repository.save(answer_submission)

        self.assertEqual(context.exception.question_id, 99)
