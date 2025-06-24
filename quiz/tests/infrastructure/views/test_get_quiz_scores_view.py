import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.application.get_quiz_scores.get_quiz_scores_response import GetQuizScoresResponse
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException
from quiz.infrastructure.views.get_quiz_scores_view import GetQuizScoresView
from user.domain.user import User


class TestGetQuizScoresView(unittest.TestCase):
    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_query_handler = Mock()
        self.mock_logger = Mock()
        self.view = GetQuizScoresView(query_handler=self.mock_query_handler, logger=self.mock_logger)

    def test_get_success(self):
        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="JavaScript Fundamentals",
            total_participants=25,
            average_score=78.5,
            max_score=95.0,
            min_score=45.0,
            top_scorer_email="top_student@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(self.quiz_id))
        self.assertEqual(response.data["quiz_title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["total_participants"], 25)
        self.assertEqual(response.data["average_score"], 78.5)
        self.assertEqual(response.data["max_score"], 95.0)
        self.assertEqual(response.data["min_score"], 45.0)
        self.assertEqual(response.data["top_scorer_email"], "top_student@example.com")

        self.mock_query_handler.handle.assert_called_once()
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.quiz_id, str(self.quiz_id))
        self.assertEqual(query_arg.requester_id, str(self.user_id))

    def test_get_handles_quiz_not_found_exception(self):
        self.mock_query_handler.handle.side_effect = QuizNotFoundException(str(self.quiz_id))

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_handles_unauthorized_quiz_access_exception(self):
        self.mock_query_handler.handle.side_effect = UnauthorizedQuizAccessException(
            quiz_id=str(self.quiz_id), user_id=str(self.user_id)
        )

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_handles_unexpected_exception(self):
        self.mock_query_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when getting quiz scores")

    def test_get_with_different_quiz_id(self):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        mock_response = GetQuizScoresResponse(
            quiz_id=str(different_quiz_id),
            quiz_title="Python Advanced",
            total_participants=30,
            average_score=82.0,
            max_score=98.0,
            min_score=55.0,
            top_scorer_email="python_expert@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, different_quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(different_quiz_id))
        self.assertEqual(response.data["quiz_title"], "Python Advanced")

        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.quiz_id, str(different_quiz_id))

    def test_get_with_different_user(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id

        different_request = Mock()
        different_request.user = different_user

        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Django Basics",
            total_participants=15,
            average_score=70.0,
            max_score=90.0,
            min_score=40.0,
            top_scorer_email="django_master@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(different_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.requester_id, str(different_user_id))

    def test_get_with_high_scores(self):
        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Easy Quiz",
            total_participants=10,
            average_score=95.0,
            max_score=100.0,
            min_score=90.0,
            top_scorer_email="perfect_student@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_score"], 95.0)
        self.assertEqual(response.data["max_score"], 100.0)
        self.assertEqual(response.data["min_score"], 90.0)

    def test_get_with_low_scores(self):
        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Challenging Quiz",
            total_participants=20,
            average_score=35.5,
            max_score=60.0,
            min_score=10.0,
            top_scorer_email="best_of_worst@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_score"], 35.5)
        self.assertEqual(response.data["max_score"], 60.0)
        self.assertEqual(response.data["min_score"], 10.0)

    def test_get_with_single_participant(self):
        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Solo Quiz",
            total_participants=1,
            average_score=88.0,
            max_score=88.0,
            min_score=88.0,
            top_scorer_email="only_participant@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_participants"], 1)
        self.assertEqual(response.data["average_score"], 88.0)
        self.assertEqual(response.data["max_score"], 88.0)
        self.assertEqual(response.data["min_score"], 88.0)

    def test_get_with_many_participants(self):
        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Popular Quiz",
            total_participants=100,
            average_score=72.3,
            max_score=99.0,
            min_score=25.0,
            top_scorer_email="quiz_champion@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_participants"], 100)
        self.assertEqual(response.data["quiz_title"], "Popular Quiz")
        self.assertEqual(response.data["top_scorer_email"], "quiz_champion@example.com")

    def test_get_with_perfect_scores(self):
        mock_response = GetQuizScoresResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Perfect Quiz",
            total_participants=5,
            average_score=100.0,
            max_score=100.0,
            min_score=100.0,
            top_scorer_email="perfectionist@example.com",
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["average_score"], 100.0)
        self.assertEqual(response.data["max_score"], 100.0)
        self.assertEqual(response.data["min_score"], 100.0)
