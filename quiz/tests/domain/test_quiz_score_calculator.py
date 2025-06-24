import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.domain.participation.quiz_score_calculator import QuizScoreCalculator
from quiz.domain.quiz.question_repository import QuestionRepository
from quiz.domain.quiz.answer_repository import AnswerRepository
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.answer import Answer
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.answer_submission import AnswerSubmission
from quiz.domain.participation.duplicate_answer_submission_exception import DuplicateAnswerSubmissionException
from quiz.domain.quiz.invalid_question_for_quiz_exception import InvalidQuestionForQuizException
from quiz.domain.quiz.invalid_answer_for_question_exception import InvalidAnswerForQuestionException
from quiz.domain.participation.quiz_score_result import QuizScoreResult, SubmittedAnswer


@patch("quiz.domain.participation.quiz_score_calculator.AnswerSubmission")
class TestQuizScoreCalculator(unittest.TestCase):
    def setUp(self):
        self.mock_question_repository = Mock(spec=QuestionRepository)
        self.mock_answer_repository = Mock(spec=AnswerRepository)

        self.calculator = QuizScoreCalculator(self.mock_question_repository, self.mock_answer_repository)

        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.id = self.quiz_id

        self.mock_participation = Mock(spec=Participation)

        self.question1 = Mock(spec=Question)
        self.question1.id = 1
        self.question1.quiz_id = self.quiz_id
        self.question1.points = 2

        self.question2 = Mock(spec=Question)
        self.question2.id = 2
        self.question2.quiz_id = self.quiz_id
        self.question2.points = 3

        self.correct_answer1 = Mock(spec=Answer)
        self.correct_answer1.id = 101
        self.correct_answer1.question_id = 1
        self.correct_answer1.is_correct = True

        self.incorrect_answer1 = Mock(spec=Answer)
        self.incorrect_answer1.id = 102
        self.incorrect_answer1.question_id = 1
        self.incorrect_answer1.is_correct = False

        self.correct_answer2 = Mock(spec=Answer)
        self.correct_answer2.id = 201
        self.correct_answer2.question_id = 2
        self.correct_answer2.is_correct = True

    def test_calculate_with_all_correct_answers_returns_full_score(self, mock_answer_submission):
        mock_submission1 = Mock(spec=AnswerSubmission)
        mock_submission1.question = self.question1
        mock_submission1.selected_answer = self.correct_answer1
        mock_submission1.is_correct = True
        mock_submission2 = Mock(spec=AnswerSubmission)
        mock_submission2.question = self.question2
        mock_submission2.selected_answer = self.correct_answer2
        mock_submission2.is_correct = True
        mock_answer_submission.side_effect = [mock_submission1, mock_submission2]

        submitted_answers = [
            SubmittedAnswer(question_id=1, answer_id=101),
            SubmittedAnswer(question_id=2, answer_id=201),
        ]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1, 2: self.question2}
        self.mock_answer_repository.find_by_ids.return_value = {101: self.correct_answer1, 201: self.correct_answer2}

        result = self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertIsInstance(result, QuizScoreResult)
        self.assertEqual(result.total_score, 5)
        self.assertEqual(result.total_possible_score, 5)
        self.assertEqual(len(result.answer_submissions), 2)

    def test_calculate_with_some_incorrect_answers_returns_partial_score(self, mock_answer_submission):
        mock_submission1 = Mock(spec=AnswerSubmission)
        mock_submission1.question = self.question1
        mock_submission1.selected_answer = self.incorrect_answer1
        mock_submission1.is_correct = False
        mock_submission2 = Mock(spec=AnswerSubmission)
        mock_submission2.question = self.question2
        mock_submission2.selected_answer = self.correct_answer2
        mock_submission2.is_correct = True
        mock_answer_submission.side_effect = [mock_submission1, mock_submission2]

        submitted_answers = [
            SubmittedAnswer(question_id=1, answer_id=102),
            SubmittedAnswer(question_id=2, answer_id=201),
        ]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1, 2: self.question2}
        self.mock_answer_repository.find_by_ids.return_value = {102: self.incorrect_answer1, 201: self.correct_answer2}

        result = self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(result.total_score, 3)
        self.assertEqual(result.total_possible_score, 5)

    def test_calculate_with_all_incorrect_answers_returns_zero_score(self, mock_answer_submission):
        mock_submission = Mock(spec=AnswerSubmission)
        mock_submission.question = self.question1
        mock_submission.selected_answer = self.incorrect_answer1
        mock_submission.is_correct = False
        mock_answer_submission.return_value = mock_submission

        submitted_answers = [
            SubmittedAnswer(question_id=1, answer_id=102),
        ]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1}
        self.mock_answer_repository.find_by_ids.return_value = {102: self.incorrect_answer1}

        result = self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(result.total_score, 0)
        self.assertEqual(result.total_possible_score, 2)

    def test_calculate_with_duplicate_question_submissions_raises_exception(self, mock_answer_submission):
        submitted_answers = [
            SubmittedAnswer(question_id=1, answer_id=101),
            SubmittedAnswer(question_id=1, answer_id=102),
        ]

        with self.assertRaises(DuplicateAnswerSubmissionException) as context:
            self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(context.exception.question_id, 1)

    def test_calculate_with_question_not_belonging_to_quiz_raises_exception(self, mock_answer_submission):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        wrong_question = Mock(spec=Question)
        wrong_question.id = 999
        wrong_question.quiz_id = different_quiz_id

        submitted_answers = [SubmittedAnswer(question_id=999, answer_id=101)]

        self.mock_question_repository.find_by_ids.return_value = {999: wrong_question}
        self.mock_answer_repository.find_by_ids.return_value = {101: self.correct_answer1}

        with self.assertRaises(InvalidQuestionForQuizException) as context:
            self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(context.exception.question_id, 999)
        self.assertEqual(context.exception.quiz_id, self.quiz_id)

    def test_calculate_with_missing_question_raises_exception(self, mock_answer_submission):
        submitted_answers = [SubmittedAnswer(question_id=999, answer_id=101)]

        self.mock_question_repository.find_by_ids.return_value = {}
        self.mock_answer_repository.find_by_ids.return_value = {101: self.correct_answer1}

        with self.assertRaises(InvalidQuestionForQuizException):
            self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

    def test_calculate_with_answer_not_belonging_to_question_raises_exception(self, mock_answer_submission):
        wrong_answer = Mock(spec=Answer)
        wrong_answer.id = 999
        wrong_answer.question_id = 999

        submitted_answers = [SubmittedAnswer(question_id=1, answer_id=999)]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1}
        self.mock_answer_repository.find_by_ids.return_value = {999: wrong_answer}

        with self.assertRaises(InvalidAnswerForQuestionException) as context:
            self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(context.exception.answer_id, 999)
        self.assertEqual(context.exception.question_id, 1)

    def test_calculate_with_missing_answer_raises_exception(self, mock_answer_submission):
        submitted_answers = [SubmittedAnswer(question_id=1, answer_id=999)]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1}
        self.mock_answer_repository.find_by_ids.return_value = {}

        with self.assertRaises(InvalidAnswerForQuestionException):
            self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

    def test_calculate_calls_repositories_with_correct_ids(self, mock_answer_submission):
        mock_submission1 = Mock(spec=AnswerSubmission)
        mock_submission1.question = self.question1
        mock_submission1.selected_answer = self.correct_answer1
        mock_submission2 = Mock(spec=AnswerSubmission)
        mock_submission2.question = self.question2
        mock_submission2.selected_answer = self.correct_answer2
        mock_answer_submission.side_effect = [mock_submission1, mock_submission2]

        submitted_answers = [
            SubmittedAnswer(question_id=1, answer_id=101),
            SubmittedAnswer(question_id=2, answer_id=201),
        ]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1, 2: self.question2}
        self.mock_answer_repository.find_by_ids.return_value = {101: self.correct_answer1, 201: self.correct_answer2}

        self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.mock_question_repository.find_by_ids.assert_called_once_with([1, 2])
        self.mock_answer_repository.find_by_ids.assert_called_once_with([101, 201])

    def test_calculate_creates_answer_submissions_with_correct_data(self, mock_answer_submission):
        mock_submission = Mock(spec=AnswerSubmission)
        mock_submission.participation = self.mock_participation
        mock_submission.question = self.question1
        mock_submission.selected_answer = self.correct_answer1
        mock_answer_submission.return_value = mock_submission

        submitted_answers = [SubmittedAnswer(question_id=1, answer_id=101)]

        self.mock_question_repository.find_by_ids.return_value = {1: self.question1}
        self.mock_answer_repository.find_by_ids.return_value = {101: self.correct_answer1}

        result = self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(len(result.answer_submissions), 1)
        submission = result.answer_submissions[0]
        self.assertEqual(submission, mock_submission)
        self.assertEqual(submission.participation, self.mock_participation)
        self.assertEqual(submission.question, self.question1)
        self.assertEqual(submission.selected_answer, self.correct_answer1)

        mock_answer_submission.assert_called_once_with(
            participation=self.mock_participation, question=self.question1, selected_answer=self.correct_answer1
        )

    def test_calculate_with_empty_submissions_returns_zero_score(self, mock_answer_submission):
        submitted_answers = []

        self.mock_question_repository.find_by_ids.return_value = {}
        self.mock_answer_repository.find_by_ids.return_value = {}

        result = self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(result.total_score, 0)
        self.assertEqual(result.total_possible_score, 0)
        self.assertEqual(len(result.answer_submissions), 0)

    def test_calculate_with_different_point_values(self, mock_answer_submission):
        mock_submission = Mock(spec=AnswerSubmission)

        high_value_question = Mock(spec=Question)
        high_value_question.id = 3
        high_value_question.quiz_id = self.quiz_id
        high_value_question.points = 10

        correct_answer3 = Mock(spec=Answer)
        correct_answer3.id = 301
        correct_answer3.question_id = 3
        correct_answer3.is_correct = True

        mock_submission.question = high_value_question
        mock_submission.selected_answer = correct_answer3
        mock_answer_submission.return_value = mock_submission

        submitted_answers = [SubmittedAnswer(question_id=3, answer_id=301)]

        self.mock_question_repository.find_by_ids.return_value = {3: high_value_question}
        self.mock_answer_repository.find_by_ids.return_value = {301: correct_answer3}

        result = self.calculator.calculate(self.mock_quiz, self.mock_participation, submitted_answers)

        self.assertEqual(result.total_score, 10)
        self.assertEqual(result.total_possible_score, 10)
