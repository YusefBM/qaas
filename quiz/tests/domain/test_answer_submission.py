import unittest
from unittest.mock import Mock

from quiz.domain.participation.answer_submission import AnswerSubmission
from quiz.domain.participation.participation import Participation
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.question import Question


class TestAnswerSubmission(unittest.TestCase):
    def setUp(self):
        self.mock_participation = Mock(spec=Participation)
        self.mock_participation.participant.email = "test@example.com"

        self.mock_question = Mock(spec=Question)
        self.mock_question.text = "What is the capital of France?"

        self.mock_correct_answer = Mock(spec=Answer)
        self.mock_correct_answer.text = "Paris"
        self.mock_correct_answer.is_correct = True

        self.mock_incorrect_answer = Mock(spec=Answer)
        self.mock_incorrect_answer.text = "London"
        self.mock_incorrect_answer.is_correct = False

        self.answer_submission = Mock(spec=AnswerSubmission)
        self.answer_submission.participation = self.mock_participation
        self.answer_submission.question = self.mock_question

    def test_is_correct_returns_true_when_answer_is_correct(self):
        self.answer_submission.selected_answer = self.mock_correct_answer
        self.answer_submission.is_correct = True

        is_correct = self.answer_submission.is_correct

        self.assertTrue(is_correct)

    def test_is_correct_returns_false_when_answer_is_incorrect(self):
        self.answer_submission.selected_answer = self.mock_incorrect_answer
        self.answer_submission.is_correct = False

        is_correct = self.answer_submission.is_correct

        self.assertFalse(is_correct)

    def test_str_returns_formatted_representation(self):
        self.answer_submission.selected_answer = self.mock_correct_answer
        self.answer_submission.__str__ = Mock(return_value="test@example.com - What is the capital of Fra - Paris")

        result = str(self.answer_submission)

        self.assertEqual(result, "test@example.com - What is the capital of Fra - Paris")

    def test_str_truncates_long_question_text_to_thirty_chars(self):
        self.mock_question.text = "This is a very long question text that should be truncated at thirty characters"
        self.answer_submission.selected_answer = self.mock_correct_answer
        self.answer_submission.__str__ = Mock(return_value="test@example.com - This is a very long question  - Paris")

        result = str(self.answer_submission)

        self.assertEqual(result, "test@example.com - This is a very long question  - Paris")

    def test_str_truncates_long_answer_text_to_twenty_chars(self):
        self.mock_correct_answer.text = "This is a very long answer text that should be truncated"
        self.answer_submission.selected_answer = self.mock_correct_answer
        self.answer_submission.__str__ = Mock(
            return_value="test@example.com - What is the capital of Fra - This is a very long "
        )

        result = str(self.answer_submission)

        self.assertEqual(result, "test@example.com - What is the capital of Fra - This is a very long ")

    def test_str_truncates_both_question_and_answer_text(self):
        self.mock_question.text = "This is a very long question text that definitely exceeds thirty characters limit"
        self.mock_correct_answer.text = "This is also a very long answer text that exceeds twenty characters"
        self.answer_submission.selected_answer = self.mock_correct_answer
        self.answer_submission.__str__ = Mock(
            return_value="test@example.com - This is a very long question  - This is also a very"
        )

        result = str(self.answer_submission)

        self.assertEqual(result, "test@example.com - This is a very long question  - This is also a very")
