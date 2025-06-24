import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.application.get_creator_quizzes.get_creator_quizzes_response import GetCreatorQuizzesResponse, QuizSummary
from quiz.infrastructure.views.get_creator_quizzes_view import GetCreatorQuizzesView
from user.domain.user import User


class TestGetCreatorQuizzesView(unittest.TestCase):
    def setUp(self):
        self.creator_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_query_handler = Mock()
        self.mock_logger = Mock()
        self.view = GetCreatorQuizzesView(query_handler=self.mock_query_handler, logger=self.mock_logger)

    def test_get_success_with_quizzes(self):
        quiz_summary_1 = QuizSummary(
            id=UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
            title="JavaScript Fundamentals",
            description="Learn the basics of JavaScript",
            questions_count=5,
            participants_count=10,
            created_at="2024-01-15T10:30:00.000000Z",
            updated_at="2024-01-15T10:30:00.000000Z",
        )
        quiz_summary_2 = QuizSummary(
            id=UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff"),
            title="Python Advanced",
            description="Advanced Python concepts",
            questions_count=8,
            participants_count=15,
            created_at="2024-01-20T14:15:00.000000Z",
            updated_at="2024-01-20T14:15:00.000000Z",
        )

        mock_response = GetCreatorQuizzesResponse(
            creator_id=str(self.creator_id), quizzes=[quiz_summary_1, quiz_summary_2], total_count=2
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.creator_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["creator_id"], str(self.creator_id))
        self.assertEqual(response.data["total_count"], 2)
        self.assertEqual(len(response.data["quizzes"]), 2)
        self.assertEqual(response.data["quizzes"][0]["title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["quizzes"][1]["title"], "Python Advanced")
        self.assertEqual(response.data["quizzes"][0]["questions_count"], 5)
        self.assertEqual(response.data["quizzes"][1]["participants_count"], 15)

        self.mock_query_handler.handle.assert_called_once()
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.creator_id, str(self.creator_id))

    def test_get_success_with_empty_quizzes(self):
        mock_response = GetCreatorQuizzesResponse(creator_id=str(self.creator_id), quizzes=[], total_count=0)

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.creator_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["creator_id"], str(self.creator_id))
        self.assertEqual(response.data["total_count"], 0)
        self.assertEqual(len(response.data["quizzes"]), 0)
        self.assertEqual(response.data["quizzes"], [])

    def test_get_handles_unexpected_exception(self):
        self.mock_query_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.get(self.mock_request, self.creator_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when getting user's quizzes")

    def test_get_with_different_creator_id(self):
        different_creator_id = UUID("99999999-8888-7777-6666-555555555555")
        quiz_summary = QuizSummary(
            id=UUID("cccccccc-dddd-eeee-ffff-000000000000"),
            title="Django Basics",
            description="Basic Django concepts",
            questions_count=3,
            participants_count=5,
            created_at="2024-01-25T09:00:00.000000Z",
            updated_at="2024-01-25T09:00:00.000000Z",
        )

        mock_response = GetCreatorQuizzesResponse(
            creator_id=str(different_creator_id), quizzes=[quiz_summary], total_count=1
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, different_creator_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quizzes"][0]["title"], "Django Basics")

        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.creator_id, str(different_creator_id))

    def test_get_with_single_quiz(self):
        quiz_summary = QuizSummary(
            id=UUID("dddddddd-eeee-ffff-0000-111111111111"),
            title="React Components",
            description="Understanding React components",
            questions_count=12,
            participants_count=25,
            created_at="2024-02-01T16:45:00.000000Z",
            updated_at="2024-02-01T16:45:00.000000Z",
        )

        mock_response = GetCreatorQuizzesResponse(
            creator_id=str(self.creator_id), quizzes=[quiz_summary], total_count=1
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.creator_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 1)
        self.assertEqual(len(response.data["quizzes"]), 1)
        self.assertEqual(response.data["quizzes"][0]["id"], str(UUID("dddddddd-eeee-ffff-0000-111111111111")))
        self.assertEqual(response.data["quizzes"][0]["questions_count"], 12)
        self.assertEqual(response.data["quizzes"][0]["participants_count"], 25)

    def test_get_with_multiple_quizzes_verifies_order(self):
        quiz_1 = QuizSummary(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            title="First Quiz",
            description="First description",
            questions_count=1,
            participants_count=1,
            created_at="2024-01-10T08:00:00.000000Z",
            updated_at="2024-01-10T08:00:00.000000Z",
        )
        quiz_2 = QuizSummary(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            title="Second Quiz",
            description="Second description",
            questions_count=2,
            participants_count=2,
            created_at="2024-01-11T09:00:00.000000Z",
            updated_at="2024-01-11T09:00:00.000000Z",
        )
        quiz_3 = QuizSummary(
            id=UUID("33333333-3333-3333-3333-333333333333"),
            title="Third Quiz",
            description="Third description",
            questions_count=3,
            participants_count=3,
            created_at="2024-01-12T10:00:00.000000Z",
            updated_at="2024-01-12T10:00:00.000000Z",
        )

        mock_response = GetCreatorQuizzesResponse(
            creator_id=str(self.creator_id), quizzes=[quiz_1, quiz_2, quiz_3], total_count=3
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.creator_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 3)
        self.assertEqual(len(response.data["quizzes"]), 3)

        quiz_ids = [quiz["id"] for quiz in response.data["quizzes"]]
        expected_ids = [
            str(UUID("11111111-1111-1111-1111-111111111111")),
            str(UUID("22222222-2222-2222-2222-222222222222")),
            str(UUID("33333333-3333-3333-3333-333333333333")),
        ]
        self.assertEqual(quiz_ids, expected_ids)

        quiz_titles = [quiz["title"] for quiz in response.data["quizzes"]]
        self.assertEqual(quiz_titles, ["First Quiz", "Second Quiz", "Third Quiz"])
