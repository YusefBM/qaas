import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.application.create_quiz.answer_data import AnswerData
from quiz.application.create_quiz.create_quiz_command import CreateQuizCommand
from quiz.application.create_quiz.create_quiz_command_handler import CreateQuizCommandHandler
from quiz.application.create_quiz.create_quiz_response import CreateQuizResponse
from quiz.application.create_quiz.question_data import QuestionData
from quiz.application.create_quiz.question_mapper import QuestionMapper
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.answer_repository import AnswerRepository
from quiz.domain.quiz.invalid_number_of_answers_exception import InvalidNumberOfAnswersException
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.question_repository import QuestionRepository
from quiz.domain.quiz.question_validator import QuestionValidator
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_repository import QuizRepository
from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException
from user.domain.user_repository import UserRepository


class TestCreateQuizCommandHandler(unittest.TestCase):
    def setUp(self):
        self.user_repository_mock = Mock(spec=UserRepository)
        self.quiz_repository_mock = Mock(spec=QuizRepository)
        self.question_repository_mock = Mock(spec=QuestionRepository)
        self.answer_repository_mock = Mock(spec=AnswerRepository)
        self.question_mapper_mock = Mock(spec=QuestionMapper)
        self.question_validator_mock = Mock(spec=QuestionValidator)

        self.handler = CreateQuizCommandHandler(
            user_repository=self.user_repository_mock,
            quiz_repository=self.quiz_repository_mock,
            question_repository=self.question_repository_mock,
            answer_repository=self.answer_repository_mock,
            question_mapper=self.question_mapper_mock,
            question_validator=self.question_validator_mock,
        )

        self.creator_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.quiz_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.question_id = UUID("11111111-2222-3333-4444-555555555555")
        self.answer_id = UUID("99999999-8888-7777-6666-555555555555")

        self.answer_data = AnswerData(text="Test Answer", is_correct=True, order=1)
        self.question_data = QuestionData(text="Test Question", order=1, points=10, answers=[self.answer_data])

        self.command = CreateQuizCommand(
            title="Test Quiz",
            description="Test Description",
            creator_id=self.creator_id,
            questions=[self.question_data],
        )

    @patch("quiz.application.create_quiz.create_quiz_command_handler.transaction")
    @patch("quiz.application.create_quiz.create_quiz_command_handler.uuid7")
    def test_handle_success(self, mock_uuid7, mock_transaction):
        mock_creator = Mock(spec=User)
        mock_creator.id = self.creator_id
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_question = Mock(spec=Question)
        mock_question.id = self.question_id
        mock_answer = Mock(spec=Answer)
        mock_answer.id = self.answer_id
        self.user_repository_mock.find_or_fail_by_id.return_value = mock_creator
        mock_uuid7.return_value = self.quiz_id
        mock_transaction.atomic.return_value.__enter__ = Mock()
        mock_transaction.atomic.return_value.__exit__ = Mock()
        self.question_mapper_mock.map_to_domain.return_value = (mock_question, [mock_answer])

        with patch("quiz.application.create_quiz.create_quiz_command_handler.Quiz", return_value=mock_quiz):
            result = self.handler.handle(self.command)

        self.assertIsInstance(result, CreateQuizResponse)
        self.assertEqual(result.quiz_id, str(self.quiz_id))
        self.user_repository_mock.find_or_fail_by_id.assert_called_once_with(user_id=self.creator_id)
        self.question_mapper_mock.map_to_domain.assert_called_once_with(mock_quiz, self.question_data)
        self.question_validator_mock.validate.assert_called_once()
        self.quiz_repository_mock.save.assert_called_once_with(mock_quiz)
        self.question_repository_mock.save.assert_called_once_with(mock_question)
        self.answer_repository_mock.bulk_save.assert_called_once_with([mock_answer])

    def test_handle_user_not_found_raises_exception(self):
        self.user_repository_mock.find_or_fail_by_id.side_effect = UserNotFoundException(str(self.creator_id))

        with self.assertRaises(UserNotFoundException):
            self.handler.handle(self.command)

        self.quiz_repository_mock.save.assert_not_called()
        self.question_repository_mock.save.assert_not_called()

    @patch("quiz.application.create_quiz.create_quiz_command_handler.uuid7")
    def test_handle_validation_error_raises_exception(self, mock_uuid7):
        mock_creator = Mock(spec=User)
        mock_creator.id = self.creator_id

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id

        mock_question = Mock(spec=Question)
        mock_answer = Mock(spec=Answer)

        self.user_repository_mock.find_or_fail_by_id.return_value = mock_creator
        mock_uuid7.return_value = self.quiz_id
        self.question_mapper_mock.map_to_domain.return_value = (mock_question, [mock_answer])
        self.question_validator_mock.validate.side_effect = InvalidNumberOfAnswersException(str(self.quiz_id))

        with patch("quiz.application.create_quiz.create_quiz_command_handler.Quiz", return_value=mock_quiz):
            with self.assertRaises(InvalidNumberOfAnswersException):
                self.handler.handle(self.command)

        self.quiz_repository_mock.save.assert_not_called()
        self.question_repository_mock.save.assert_not_called()
