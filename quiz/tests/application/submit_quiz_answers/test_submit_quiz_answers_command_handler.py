import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.application.submit_quiz_answers.submit_quiz_answers_command import SubmitQuizAnswersCommand, SubmittedAnswer
from quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler import SubmitQuizAnswersCommandHandler
from quiz.application.submit_quiz_answers.submit_quiz_answers_response import SubmitQuizAnswersResponse
from quiz.domain.participation.answer_submission_repository import AnswerSubmissionRepository
from quiz.domain.participation.incomplete_quiz_submission_exception import IncompleteQuizSubmissionException
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.participation.quiz_already_completed_exception import QuizAlreadyCompletedException
from quiz.domain.participation.quiz_score_calculator import QuizScoreCalculator, QuizScoreResult
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_repository import QuizRepository


class TestSubmitQuizAnswersCommandHandler(unittest.TestCase):
    def setUp(self):
        self.quiz_repository_mock = Mock(spec=QuizRepository)
        self.participation_repository_mock = Mock(spec=ParticipationRepository)
        self.answer_submission_repository_mock = Mock(spec=AnswerSubmissionRepository)
        self.quiz_score_calculator_mock = Mock(spec=QuizScoreCalculator)

        self.handler = SubmitQuizAnswersCommandHandler(
            quiz_repository=self.quiz_repository_mock,
            participation_repository=self.participation_repository_mock,
            answer_submission_repository=self.answer_submission_repository_mock,
            quiz_score_calculator=self.quiz_score_calculator_mock,
        )

        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.participant_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participation_id = UUID("11111111-2222-3333-4444-555555555555")

        self.submitted_answer_1 = SubmittedAnswer(question_id=1, answer_id=1)
        self.submitted_answer_2 = SubmittedAnswer(question_id=2, answer_id=3)

        self.command = SubmitQuizAnswersCommand(
            participant_id=self.participant_id,
            quiz_id=self.quiz_id,
            answers=[self.submitted_answer_1, self.submitted_answer_2],
        )

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_success(self, mock_transaction):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "JavaScript Fundamentals"
        mock_quiz.total_questions = 2

        mock_participation = Mock(spec=Participation)
        mock_participation.id = self.participation_id
        mock_participation.is_completed.return_value = False
        mock_participation.get_formatted_completed_at.return_value = "2024-01-15T14:30:00Z"

        mock_score_result = Mock(spec=QuizScoreResult)
        mock_score_result.total_score = 85
        mock_score_result.total_possible_score = 100
        mock_score_result.answer_submissions = []

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.return_value = mock_participation
        self.quiz_score_calculator_mock.calculate.return_value = mock_score_result

        result = self.handler.handle(self.command)

        self.assertIsInstance(result, SubmitQuizAnswersResponse)
        self.assertEqual(result.message, "Quiz completed successfully")
        self.assertEqual(result.participation_id, self.participation_id)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "JavaScript Fundamentals")
        self.assertEqual(result.score, 85)
        self.assertEqual(result.total_possible_score, 100)
        self.assertEqual(result.completed_at, "2024-01-15T14:30:00Z")

        self.quiz_repository_mock.find_or_fail_by_id.assert_called_once_with(
            UUID("12345678-1234-5678-9abc-123456789abc")
        )
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.assert_called_once_with(
            self.quiz_id, self.participant_id
        )
        mock_participation.complete.assert_called_once_with(score=85)
        self.answer_submission_repository_mock.bulk_save.assert_called_once_with([])
        self.participation_repository_mock.save.assert_called_once_with(mock_participation)

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_quiz_not_found_raises_exception(self, mock_transaction):
        from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.side_effect = QuizNotFoundException(
            "12345678-1234-5678-9abc-123456789abc"
        )

        with self.assertRaises(QuizNotFoundException):
            self.handler.handle(self.command)

        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.assert_not_called()
        self.participation_repository_mock.save.assert_not_called()

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_participation_not_found_raises_exception(self, mock_transaction):
        from quiz.domain.participation.participation_not_found_for_quiz_and_participant_exception import (
            ParticipationNotFoundForQuizAndParticipantException,
        )

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.total_questions = 2

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.side_effect = (
            ParticipationNotFoundForQuizAndParticipantException(self.quiz_id, self.participant_id)
        )

        with self.assertRaises(ParticipationNotFoundForQuizAndParticipantException):
            self.handler.handle(self.command)

        self.participation_repository_mock.save.assert_not_called()

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_quiz_already_completed_raises_exception(self, mock_transaction):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.total_questions = 2

        mock_participation = Mock(spec=Participation)
        mock_participation.is_completed.return_value = True

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.return_value = mock_participation

        with self.assertRaises(QuizAlreadyCompletedException):
            self.handler.handle(self.command)

        self.participation_repository_mock.save.assert_not_called()

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_incomplete_quiz_submission_raises_exception(self, mock_transaction):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.total_questions = 3  # Expecting 3 answers but command has only 2

        mock_participation = Mock(spec=Participation)
        mock_participation.is_completed.return_value = False

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.return_value = mock_participation

        with self.assertRaises(IncompleteQuizSubmissionException):
            self.handler.handle(self.command)

        self.participation_repository_mock.save.assert_not_called()

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_single_question_quiz(self, mock_transaction):
        single_answer_command = SubmitQuizAnswersCommand(
            participant_id=self.participant_id, quiz_id=self.quiz_id, answers=[self.submitted_answer_1]
        )

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Single Question Quiz"
        mock_quiz.total_questions = 1

        mock_participation = Mock(spec=Participation)
        mock_participation.id = self.participation_id
        mock_participation.is_completed.return_value = False
        mock_participation.get_formatted_completed_at.return_value = "2024-01-15T15:00:00Z"

        mock_score_result = Mock(spec=QuizScoreResult)
        mock_score_result.total_score = 100
        mock_score_result.total_possible_score = 100
        mock_score_result.answer_submissions = []

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.return_value = mock_participation
        self.quiz_score_calculator_mock.calculate.return_value = mock_score_result

        result = self.handler.handle(single_answer_command)

        self.assertEqual(result.score, 100)
        self.assertEqual(result.total_possible_score, 100)
        self.assertEqual(result.quiz_title, "Single Question Quiz")

    @patch("quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler.transaction")
    def test_handle_zero_score(self, mock_transaction):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Failed Quiz"
        mock_quiz.total_questions = 2

        mock_participation = Mock(spec=Participation)
        mock_participation.id = self.participation_id
        mock_participation.is_completed.return_value = False
        mock_participation.get_formatted_completed_at.return_value = "2024-01-15T16:00:00Z"

        mock_score_result = Mock(spec=QuizScoreResult)
        mock_score_result.total_score = 0
        mock_score_result.total_possible_score = 100
        mock_score_result.answer_submissions = []

        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_repository_mock.find_or_fail_by_quiz_and_participant.return_value = mock_participation
        self.quiz_score_calculator_mock.calculate.return_value = mock_score_result

        result = self.handler.handle(self.command)

        self.assertEqual(result.score, 0)
        self.assertEqual(result.total_possible_score, 100)
        mock_participation.complete.assert_called_once_with(score=0)

    def test_response_as_dict_structure(self):
        response = SubmitQuizAnswersResponse(
            message="Quiz completed successfully",
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Test Quiz",
            score=90,
            total_possible_score=100,
            completed_at="2024-01-15T17:00:00Z",
        )

        result_dict = response.as_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["message"], "Quiz completed successfully")
        self.assertEqual(result_dict["participation_id"], str(self.participation_id))
        self.assertEqual(result_dict["quiz_id"], str(self.quiz_id))
        self.assertEqual(result_dict["quiz_title"], "Test Quiz")
        self.assertEqual(result_dict["score"], 90)
        self.assertEqual(result_dict["total_possible_score"], 100)
        self.assertEqual(result_dict["completed_at"], "2024-01-15T17:00:00Z")
