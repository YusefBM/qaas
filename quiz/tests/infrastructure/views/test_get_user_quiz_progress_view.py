import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.application.get_user_quiz_progress.get_user_quiz_progress_response import (
    GetUserQuizProgressResponse,
    ParticipationData,
)
from quiz.domain.participation.participation_not_found_for_user_exception import ParticipationNotFoundForUserException
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.views.get_user_quiz_progress_view import GetUserQuizProgressView
from user.domain.user import User


class TestGetUserQuizProgressView(unittest.TestCase):
    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_query_handler = Mock()
        self.mock_logger = Mock()
        self.view = GetUserQuizProgressView(query_handler=self.mock_query_handler, logger=self.mock_logger)

    def test_get_success_completed_quiz(self):
        participation = ParticipationData(
            status="completed",
            invited_at="2024-01-15T10:30:00.000000Z",
            completed_at="2024-01-16T14:20:00.000000Z",
            score=85,
            score_percentage=85.0,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="JavaScript Fundamentals",
            quiz_description="Learn the basics of JavaScript",
            total_questions=10,
            total_possible_points=100,
            quiz_created_at="2024-01-15T09:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(self.quiz_id))
        self.assertEqual(response.data["quiz_title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["quiz_description"], "Learn the basics of JavaScript")
        self.assertEqual(response.data["total_questions"], 10)
        self.assertEqual(response.data["total_possible_points"], 100)
        self.assertEqual(response.data["quiz_created_at"], "2024-01-15T09:00:00.000000Z")
        self.assertEqual(response.data["participation"]["status"], "completed")
        self.assertEqual(response.data["participation"]["invited_at"], "2024-01-15T10:30:00.000000Z")
        self.assertEqual(response.data["participation"]["completed_at"], "2024-01-16T14:20:00.000000Z")
        self.assertEqual(response.data["participation"]["score"], 85)
        self.assertEqual(response.data["participation"]["score_percentage"], 85.0)

        self.mock_query_handler.handle.assert_called_once()
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.quiz_id, str(self.quiz_id))
        self.assertEqual(query_arg.requester_id, str(self.user_id))

    def test_get_success_invited_quiz(self):
        participation = ParticipationData(
            status="invited",
            invited_at="2024-01-20T11:00:00.000000Z",
            completed_at=None,
            score=None,
            score_percentage=None,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Python Advanced",
            quiz_description="Advanced Python concepts",
            total_questions=15,
            total_possible_points=150,
            quiz_created_at="2024-01-20T10:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_title"], "Python Advanced")
        self.assertEqual(response.data["participation"]["status"], "invited")
        self.assertEqual(response.data["participation"]["completed_at"], None)
        self.assertEqual(response.data["participation"]["score"], None)
        self.assertEqual(response.data["participation"]["score_percentage"], None)

    def test_get_success_perfect_score(self):
        participation = ParticipationData(
            status="completed",
            invited_at="2024-02-01T08:00:00.000000Z",
            completed_at="2024-02-01T09:30:00.000000Z",
            score=100,
            score_percentage=100.0,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Easy Quiz",
            quiz_description="A simple quiz for beginners",
            total_questions=5,
            total_possible_points=100,
            quiz_created_at="2024-02-01T07:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["participation"]["score"], 100)
        self.assertEqual(response.data["participation"]["score_percentage"], 100.0)

    def test_get_success_low_score(self):
        participation = ParticipationData(
            status="completed",
            invited_at="2024-02-05T14:00:00.000000Z",
            completed_at="2024-02-05T15:45:00.000000Z",
            score=25,
            score_percentage=25.0,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Challenging Quiz",
            quiz_description="A difficult quiz for experts",
            total_questions=20,
            total_possible_points=100,
            quiz_created_at="2024-02-05T13:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["participation"]["score"], 25)
        self.assertEqual(response.data["participation"]["score_percentage"], 25.0)

    def test_get_handles_quiz_not_found_exception(self):
        self.mock_query_handler.handle.side_effect = QuizNotFoundException(str(self.quiz_id))

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Quiz with ID '12345678-1234-5678-9abc-123456789abc' not found", response.data["message"])

    def test_get_handles_participation_not_found_for_user_exception(self):
        self.mock_query_handler.handle.side_effect = ParticipationNotFoundForUserException(
            quiz_id=str(self.quiz_id), user_id=str(self.user_id)
        )

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_handles_unexpected_exception(self):
        self.mock_query_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when getting user quiz progress")

    def test_get_with_different_quiz_id(self):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        participation = ParticipationData(
            status="completed",
            invited_at="2024-03-01T10:00:00.000000Z",
            completed_at="2024-03-01T11:15:00.000000Z",
            score=75,
            score_percentage=75.0,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(different_quiz_id),
            quiz_title="React Components",
            quiz_description="Understanding React components",
            total_questions=12,
            total_possible_points=100,
            quiz_created_at="2024-03-01T09:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, different_quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(different_quiz_id))
        self.assertEqual(response.data["quiz_title"], "React Components")

        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.quiz_id, str(different_quiz_id))

    def test_get_with_different_user(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id

        different_request = Mock()
        different_request.user = different_user

        participation = ParticipationData(
            status="invited",
            invited_at="2024-03-10T16:00:00.000000Z",
            completed_at=None,
            score=None,
            score_percentage=None,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Vue.js Basics",
            quiz_description="Introduction to Vue.js",
            total_questions=8,
            total_possible_points=80,
            quiz_created_at="2024-03-10T15:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(different_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.requester_id, str(different_user_id))

    def test_get_with_decimal_score_percentage(self):
        participation = ParticipationData(
            status="completed",
            invited_at="2024-03-15T12:00:00.000000Z",
            completed_at="2024-03-15T13:20:00.000000Z",
            score=83,
            score_percentage=83.33,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Mixed Questions Quiz",
            quiz_description="A quiz with various difficulty levels",
            total_questions=6,
            total_possible_points=100,
            quiz_created_at="2024-03-15T11:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["participation"]["score_percentage"], 83.33)

    def test_get_with_large_quiz(self):
        participation = ParticipationData(
            status="completed",
            invited_at="2024-04-01T09:00:00.000000Z",
            completed_at="2024-04-01T12:00:00.000000Z",
            score=450,
            score_percentage=90.0,
        )

        mock_response = GetUserQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Comprehensive Programming Quiz",
            quiz_description="A comprehensive quiz covering multiple programming languages",
            total_questions=50,
            total_possible_points=500,
            quiz_created_at="2024-04-01T08:00:00.000000Z",
            participation=participation,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_questions"], 50)
        self.assertEqual(response.data["total_possible_points"], 500)
        self.assertEqual(response.data["participation"]["score"], 450)
