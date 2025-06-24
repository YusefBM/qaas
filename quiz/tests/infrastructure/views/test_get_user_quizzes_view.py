import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.application.get_user_quizzes.get_user_quizzes_response import GetUserQuizzesResponse, QuizParticipationSummary
from quiz.infrastructure.views.get_user_quizzes_view import GetUserQuizzesView
from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException


class TestGetUserQuizzesView(unittest.TestCase):
    def setUp(self):
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_query_handler = Mock()
        self.mock_logger = Mock()
        self.view = GetUserQuizzesView(query_handler=self.mock_query_handler, logger=self.mock_logger)

    def test_get_success_with_quizzes(self):
        quiz_participation_1 = QuizParticipationSummary(
            quiz_id=self.quiz_id,
            quiz_title="JavaScript Fundamentals",
            quiz_description="Learn the basics of JavaScript",
            total_questions=5,
            total_participants=10,
            quiz_created_at="2024-01-15T10:30:00.000000Z",
            participation_status="completed",
            score=85,
            completed_at="2024-01-16T14:20:00.000000Z",
            participation_created_at="2024-01-15T11:00:00.000000Z",
        )

        quiz_participation_2 = QuizParticipationSummary(
            quiz_id=UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
            quiz_title="Python Advanced",
            quiz_description="Advanced Python concepts",
            total_questions=8,
            total_participants=15,
            quiz_created_at="2024-01-20T09:15:00.000000Z",
            participation_status="in_progress",
            participation_created_at="2024-01-20T10:00:00.000000Z",
        )

        mock_response = GetUserQuizzesResponse(
            quizzes_participations=[quiz_participation_1, quiz_participation_2], total_count=2
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 2)
        self.assertEqual(len(response.data["user_quizzes"]), 2)
        self.assertEqual(response.data["user_quizzes"][0]["quiz_title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["user_quizzes"][0]["status"], "completed")
        self.assertEqual(response.data["user_quizzes"][0]["score"], 85)
        self.assertEqual(response.data["user_quizzes"][1]["quiz_title"], "Python Advanced")
        self.assertEqual(response.data["user_quizzes"][1]["status"], "in_progress")

        self.mock_query_handler.handle.assert_called_once()
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.requester_id, self.user_id)

    def test_get_success_with_empty_quizzes(self):
        mock_response = GetUserQuizzesResponse(quizzes_participations=[], total_count=0)

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 0)
        self.assertEqual(len(response.data["user_quizzes"]), 0)
        self.assertEqual(response.data["user_quizzes"], [])

    def test_get_handles_user_not_found_exception(self):
        self.mock_query_handler.handle.side_effect = UserNotFoundException(str(self.user_id))

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_handles_unexpected_exception(self):
        self.mock_query_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when getting user's quizzes")

    def test_get_with_different_user(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id

        different_request = Mock()
        different_request.user = different_user

        quiz_participation = QuizParticipationSummary(
            quiz_id=self.quiz_id,
            quiz_title="Django Basics",
            quiz_description="Basic Django concepts",
            total_questions=3,
            total_participants=5,
            quiz_created_at="2024-01-25T08:00:00.000000Z",
            participation_status="not_started",
            participation_created_at="2024-01-25T09:00:00.000000Z",
        )

        mock_response = GetUserQuizzesResponse(quizzes_participations=[quiz_participation], total_count=1)

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(different_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.requester_id, different_user_id)

    def test_get_with_single_completed_quiz(self):
        quiz_participation = QuizParticipationSummary(
            quiz_id=self.quiz_id,
            quiz_title="React Components",
            quiz_description="Understanding React components",
            total_questions=12,
            total_participants=25,
            quiz_created_at="2024-02-01T16:45:00.000000Z",
            participation_status="completed",
            score=95,
            completed_at="2024-02-02T10:30:00.000000Z",
            participation_created_at="2024-02-01T17:00:00.000000Z",
        )

        mock_response = GetUserQuizzesResponse(quizzes_participations=[quiz_participation], total_count=1)

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 1)
        self.assertEqual(len(response.data["user_quizzes"]), 1)
        self.assertEqual(response.data["user_quizzes"][0]["quiz_title"], "React Components")
        self.assertEqual(response.data["user_quizzes"][0]["score"], 95)
        self.assertEqual(response.data["user_quizzes"][0]["total_questions"], 12)

    def test_get_with_quiz_without_score(self):
        quiz_participation = QuizParticipationSummary(
            quiz_id=self.quiz_id,
            quiz_title="Vue.js Basics",
            quiz_description="Introduction to Vue.js",
            total_questions=6,
            total_participants=8,
            quiz_created_at="2024-02-05T12:00:00.000000Z",
            participation_status="in_progress",
            participation_created_at="2024-02-05T13:00:00.000000Z",
        )

        mock_response = GetUserQuizzesResponse(quizzes_participations=[quiz_participation], total_count=1)

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_quizzes"][0]["score"], None)
        self.assertEqual(response.data["user_quizzes"][0]["completed_at"], None)
        self.assertEqual(response.data["user_quizzes"][0]["status"], "in_progress")

    def test_get_with_multiple_quiz_statuses(self):
        completed_quiz = QuizParticipationSummary(
            quiz_id=UUID("11111111-2222-3333-4444-555555555555"),
            quiz_title="Completed Quiz",
            quiz_description="A completed quiz",
            total_questions=4,
            total_participants=10,
            quiz_created_at="2024-01-10T08:00:00.000000Z",
            participation_status="completed",
            score=75,
            completed_at="2024-01-11T09:00:00.000000Z",
            participation_created_at="2024-01-10T08:30:00.000000Z",
        )

        in_progress_quiz = QuizParticipationSummary(
            quiz_id=UUID("22222222-3333-4444-5555-666666666666"),
            quiz_title="In Progress Quiz",
            quiz_description="A quiz in progress",
            total_questions=7,
            total_participants=12,
            quiz_created_at="2024-01-12T10:00:00.000000Z",
            participation_status="in_progress",
            participation_created_at="2024-01-12T11:00:00.000000Z",
        )

        not_started_quiz = QuizParticipationSummary(
            quiz_id=UUID("33333333-4444-5555-6666-777777777777"),
            quiz_title="Not Started Quiz",
            quiz_description="A quiz not yet started",
            total_questions=9,
            total_participants=20,
            quiz_created_at="2024-01-15T14:00:00.000000Z",
            participation_status="not_started",
            participation_created_at="2024-01-15T15:00:00.000000Z",
        )

        mock_response = GetUserQuizzesResponse(
            quizzes_participations=[completed_quiz, in_progress_quiz, not_started_quiz], total_count=3
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 3)
        self.assertEqual(len(response.data["user_quizzes"]), 3)

        quiz_statuses = [quiz["status"] for quiz in response.data["user_quizzes"]]
        self.assertEqual(quiz_statuses, ["completed", "in_progress", "not_started"])

        quiz_scores = [quiz["score"] for quiz in response.data["user_quizzes"]]
        self.assertEqual(quiz_scores, [75, None, None])
