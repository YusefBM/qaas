import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.domain.quiz.question_validator import QuestionValidator
from quiz.domain.quiz.question_validator_context import QuestionValidatorContext
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.invalid_number_of_answers_exception import InvalidNumberOfAnswersException
from quiz.domain.quiz.invalid_number_of_correct_answers_exception import InvalidNumberOfCorrectAnswersException


class TestQuestionValidator(unittest.TestCase):
    def setUp(self):
        self.validator = QuestionValidator()
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")

        self.mock_question = Mock(spec=Question)
        self.mock_question.quiz_id = self.quiz_id

    def test_validate_succeeds_with_three_answers_and_one_correct(self):
        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        self.validator.validate(context)

    def test_validate_raises_exception_with_less_than_three_answers(self):
        answers = [self.__create_answer(is_correct=True), self.__create_answer(is_correct=False)]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        with self.assertRaises(InvalidNumberOfAnswersException) as exc_context:
            self.validator.validate(context)

        self.assertEqual(exc_context.exception.quiz_id, self.quiz_id)

    def test_validate_raises_exception_with_more_than_three_answers(self):
        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        with self.assertRaises(InvalidNumberOfAnswersException) as exc_context:
            self.validator.validate(context)

        self.assertEqual(exc_context.exception.quiz_id, self.quiz_id)

    def test_validate_raises_exception_with_no_correct_answers(self):
        answers = [
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        with self.assertRaises(InvalidNumberOfCorrectAnswersException) as exc_context:
            self.validator.validate(context)

        self.assertEqual(exc_context.exception.quiz_id, self.quiz_id)

    def test_validate_raises_exception_with_multiple_correct_answers(self):
        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        with self.assertRaises(InvalidNumberOfCorrectAnswersException) as exc_context:
            self.validator.validate(context)

        self.assertEqual(exc_context.exception.quiz_id, self.quiz_id)

    def test_validate_raises_exception_with_all_correct_answers(self):
        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=True),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        with self.assertRaises(InvalidNumberOfCorrectAnswersException) as exc_context:
            self.validator.validate(context)

        self.assertEqual(exc_context.exception.quiz_id, self.quiz_id)

    def test_validate_raises_exception_with_empty_answers_list(self):
        answers = []
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        with self.assertRaises(InvalidNumberOfAnswersException) as exc_context:
            self.validator.validate(context)

        self.assertEqual(exc_context.exception.quiz_id, self.quiz_id)

    def test_validate_uses_required_number_of_answers_constant(self):
        Question.REQUIRED_NUMBER_OF_ANSWERS = 3

        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)

        self.validator.validate(context)

    def test_validate_succeeds_with_different_correct_answer_positions(self):
        first_correct = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]
        middle_correct = [
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
        ]
        last_correct = [
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=True),
        ]

        for answers in [first_correct, middle_correct, last_correct]:
            context = QuestionValidatorContext(question=self.mock_question, answers=answers)
            self.validator.validate(context)

    def test_validate_preserves_context_data_after_validation(self):
        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]
        context = QuestionValidatorContext(question=self.mock_question, answers=answers)
        original_question = context.question
        original_answers = context.answers

        self.validator.validate(context)

        self.assertEqual(context.question, original_question)
        self.assertEqual(context.answers, original_answers)

    def test_get_correct_answers_returns_single_correct_answer(self):
        answers = [
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
        ]

        correct_answers = self.validator._QuestionValidator__get_correct_answers(answers)

        self.assertEqual(len(correct_answers), 1)
        self.assertTrue(correct_answers[0].is_correct)

    def test_get_correct_answers_returns_multiple_correct_answers(self):
        answers = [
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=True),
            self.__create_answer(is_correct=False),
        ]

        correct_answers = self.validator._QuestionValidator__get_correct_answers(answers)

        self.assertEqual(len(correct_answers), 2)
        for answer in correct_answers:
            self.assertTrue(answer.is_correct)

    def test_get_correct_answers_returns_empty_list_when_none_correct(self):
        answers = [
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
            self.__create_answer(is_correct=False),
        ]

        correct_answers = self.validator._QuestionValidator__get_correct_answers(answers)

        self.assertEqual(len(correct_answers), 0)

    def __create_answer(self, is_correct: bool) -> Mock:
        answer = Mock(spec=Answer)
        answer.is_correct = is_correct
        return answer
