import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status
from voluptuous import MultipleInvalid

from quiz.application.create_quiz.create_quiz_response import CreateQuizResponse
from quiz.domain.quiz.answer_already_exists_exception import AnswerAlreadyExistsException
from quiz.domain.quiz.invalid_number_of_answers_exception import InvalidNumberOfAnswersException
from quiz.domain.quiz.invalid_number_of_correct_answers_exception import InvalidNumberOfCorrectAnswersException
from quiz.domain.quiz.question_already_exists_exception import QuestionAlreadyExistsException
from quiz.domain.quiz.quiz_already_exists_exception import QuizAlreadyExistsException
from quiz.infrastructure.views.create_quiz_view import CreateQuizView
from user.domain.user import User


class TestCreateQuizView(unittest.TestCase):
    def setUp(self):
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.quiz_id = "12345678-1234-5678-9abc-123456789abc"

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.valid_quiz_data = {
            "title": "JavaScript Fundamentals",
            "description": "Learn the basics of JavaScript",
            "questions": [
                {
                    "text": "What is JavaScript?",
                    "order": 1,
                    "points": 10,
                    "answers": [
                        {"text": "Programming language", "order": 1, "is_correct": True},
                        {"text": "Database", "order": 2, "is_correct": False},
                    ],
                }
            ],
        }

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user
        self.mock_request.data = self.valid_quiz_data

        self.mock_command_handler = Mock()
        self.mock_schema = Mock()
        self.mock_logger = Mock()
        self.view = CreateQuizView(
            command_handler=self.mock_command_handler, schema=self.mock_schema, logger=self.mock_logger
        )

    def test_post_success(self):
        mock_response = CreateQuizResponse(quiz_id=self.quiz_id)

        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], self.quiz_id)

        self.mock_command_handler.handle.assert_called_once()
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.title, "JavaScript Fundamentals")
        self.assertEqual(command_arg.description, "Learn the basics of JavaScript")
        self.assertEqual(command_arg.creator_id, str(self.user_id))
        self.assertEqual(command_arg.questions, self.valid_quiz_data["questions"])

    def test_post_handles_non_dict_request_data(self):
        self.mock_request.data = "not a dict"

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Body request must be a JSON object")

    def test_post_handles_validation_error(self):
        self.mock_schema.side_effect = MultipleInvalid("Invalid title")

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_malformed_request_body_exception(self):
        self.mock_schema.side_effect = Exception("Malformed JSON")

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Malformed request body")

    def test_post_handles_quiz_already_exists_exception(self):
        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.side_effect = QuizAlreadyExistsException(
            title="JavaScript Fundamentals", creator_id=str(self.user_id)
        )

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_handles_question_already_exists_exception(self):
        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.side_effect = QuestionAlreadyExistsException(quiz_id=self.quiz_id, order=1)

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_handles_answer_already_exists_exception(self):
        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.side_effect = AnswerAlreadyExistsException(
            order=1, question_id=UUID("12345678-1234-5678-9abc-123456789abc")
        )

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_handles_invalid_number_of_answers_exception(self):
        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.side_effect = InvalidNumberOfAnswersException(quiz_id=self.quiz_id)

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_invalid_number_of_correct_answers_exception(self):
        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.side_effect = InvalidNumberOfCorrectAnswersException(quiz_id=self.quiz_id)

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_unexpected_exception(self):
        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when creating a quiz")

    def test_post_with_different_quiz_data(self):
        different_quiz_data = {
            "title": "Python Advanced",
            "description": "Advanced Python concepts",
            "questions": [
                {
                    "text": "What is a decorator?",
                    "order": 1,
                    "points": 20,
                    "answers": [
                        {"text": "Function wrapper", "order": 1, "is_correct": True},
                        {"text": "Class method", "order": 2, "is_correct": False},
                        {"text": "Variable", "order": 3, "is_correct": False},
                    ],
                }
            ],
        }

        self.mock_request.data = different_quiz_data
        mock_response = CreateQuizResponse(quiz_id="different-quiz-id")

        self.mock_schema.return_value = different_quiz_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], "different-quiz-id")

        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.title, "Python Advanced")
        self.assertEqual(command_arg.description, "Advanced Python concepts")

    def test_post_with_different_creator(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id

        different_request = Mock()
        different_request.user = different_user
        different_request.data = self.valid_quiz_data

        mock_response = CreateQuizResponse(quiz_id=self.quiz_id)

        self.mock_schema.return_value = self.valid_quiz_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(different_request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.creator_id, str(different_user_id))

    def test_post_with_multiple_questions(self):
        multiple_questions_data = {
            "title": "Full Stack Quiz",
            "description": "Frontend and Backend questions",
            "questions": [
                {
                    "text": "What is React?",
                    "order": 1,
                    "points": 10,
                    "answers": [
                        {"text": "Library", "order": 1, "is_correct": True},
                        {"text": "Framework", "order": 2, "is_correct": False},
                    ],
                },
                {
                    "text": "What is Django?",
                    "order": 2,
                    "points": 15,
                    "answers": [
                        {"text": "Framework", "order": 1, "is_correct": True},
                        {"text": "Library", "order": 2, "is_correct": False},
                    ],
                },
            ],
        }

        self.mock_request.data = multiple_questions_data
        mock_response = CreateQuizResponse(quiz_id=self.quiz_id)

        self.mock_schema.return_value = multiple_questions_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(len(command_arg.questions), 2)
        self.assertEqual(command_arg.questions[0]["text"], "What is React?")
        self.assertEqual(command_arg.questions[1]["text"], "What is Django?")
