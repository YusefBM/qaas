import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.application.get_quiz_query.get_quiz_query_response import GetQuizQueryResponse, QuizQuestion, QuizAnswer
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException
from quiz.infrastructure.views.get_quiz_view import GetQuizView
from user.domain.user import User


class TestGetQuizView(unittest.TestCase):
    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.participant_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.question_id = UUID("11111111-2222-3333-4444-555555555555")
        self.answer_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.participant_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_query_handler = Mock()
        self.mock_logger = Mock()
        self.view = GetQuizView(query_handler=self.mock_query_handler, logger=self.mock_logger)

    def test_get_success(self):
        mock_answer = QuizAnswer(answer_id=self.answer_id, text="JavaScript", order=1)
        mock_question = QuizQuestion(
            question_id=self.question_id,
            text="What is your favorite programming language?",
            order=1,
            answers=[mock_answer],
        )
        mock_response = GetQuizQueryResponse(
            quiz_id=self.quiz_id,
            title="JavaScript Fundamentals",
            description="Learn the basics of JavaScript",
            questions=[mock_question],
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(self.quiz_id))
        self.assertEqual(response.data["title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["description"], "Learn the basics of JavaScript")
        self.assertEqual(len(response.data["questions"]), 1)
        self.assertEqual(response.data["questions"][0]["question_id"], str(self.question_id))
        self.assertEqual(response.data["questions"][0]["text"], "What is your favorite programming language?")

        self.mock_query_handler.handle.assert_called_once()
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.participant_id, self.participant_id)
        self.assertEqual(query_arg.quiz_id, self.quiz_id)

    def test_get_handles_unauthorized_quiz_access_exception(self):
        self.mock_query_handler.handle.side_effect = UnauthorizedQuizAccessException(
            quiz_id=str(self.quiz_id), user_id=str(self.participant_id)
        )

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_handles_unexpected_exception(self):
        self.mock_query_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "An unexpected error occurred")

    def test_get_with_different_quiz_id(self):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        mock_response = GetQuizQueryResponse(
            quiz_id=different_quiz_id, title="Python Advanced", description="Advanced Python concepts", questions=[]
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, different_quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(different_quiz_id))
        self.assertEqual(response.data["title"], "Python Advanced")

        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.quiz_id, different_quiz_id)

    def test_get_with_different_participant(self):
        different_participant_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_participant_id

        different_request = Mock()
        different_request.user = different_user

        mock_response = GetQuizQueryResponse(
            quiz_id=self.quiz_id, title="Django Basics", description="Basic Django concepts", questions=[]
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(different_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.participant_id, different_participant_id)

    def test_get_with_multiple_questions_and_answers(self):
        answer1 = QuizAnswer(answer_id=UUID("aaaa1111-bbbb-cccc-dddd-eeeeeeeeeeee"), text="Python", order=1)
        answer2 = QuizAnswer(answer_id=UUID("aaaa2222-bbbb-cccc-dddd-eeeeeeeeeeee"), text="JavaScript", order=2)
        answer3 = QuizAnswer(answer_id=UUID("aaaa3333-bbbb-cccc-dddd-eeeeeeeeeeee"), text="Yes", order=1)
        answer4 = QuizAnswer(answer_id=UUID("aaaa4444-bbbb-cccc-dddd-eeeeeeeeeeee"), text="No", order=2)

        question1 = QuizQuestion(
            question_id=UUID("1111aaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
            text="What is your favorite language?",
            order=1,
            answers=[answer1, answer2],
        )
        question2 = QuizQuestion(
            question_id=UUID("2222aaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
            text="Is Python interpreted?",
            order=2,
            answers=[answer3, answer4],
        )

        mock_response = GetQuizQueryResponse(
            quiz_id=self.quiz_id,
            title="Programming Quiz",
            description="Test your programming knowledge",
            questions=[question1, question2],
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["questions"]), 2)
        self.assertEqual(len(response.data["questions"][0]["answers"]), 2)
        self.assertEqual(len(response.data["questions"][1]["answers"]), 2)
        self.assertEqual(response.data["questions"][0]["text"], "What is your favorite language?")
        self.assertEqual(response.data["questions"][1]["text"], "Is Python interpreted?")
