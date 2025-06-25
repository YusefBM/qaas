import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.application.get_user_quiz_progress.get_user_quiz_progress_query import GetUserQuizProgressQuery
from quiz.application.get_user_quiz_progress.get_user_quiz_progress_query_handler import GetUserQuizProgressQueryHandler
from quiz.application.get_user_quiz_progress.get_user_quiz_progress_response import GetUserQuizProgressResponse
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.participation.participation_not_found_for_user_exception import ParticipationNotFoundForUserException
from quiz.domain.participation.user_participation_data import UserParticipationData
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.quiz_repository import QuizRepository
from user.domain.user import User


class TestGetUserQuizProgressQueryHandler(unittest.TestCase):

    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.creator_id = UUID("11111111-2222-3333-4444-555555555555")

        self.mock_quiz_repository = Mock(spec=QuizRepository)
        self.mock_participation_finder = Mock(spec=ParticipationFinder)

        self.handler = GetUserQuizProgressQueryHandler(
            quiz_repository=self.mock_quiz_repository,
            participation_finder=self.mock_participation_finder,
        )

        self.mock_creator = Mock(spec=User)
        self.mock_creator.id = self.creator_id

        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.id = self.quiz_id
        self.mock_quiz.title = "JavaScript Fundamentals"
        self.mock_quiz.description = "Learn the basics of JavaScript"
        self.mock_quiz.total_questions = 10
        self.mock_quiz.total_possible_points = 100
        self.mock_quiz.get_formatted_created_at.return_value = "2024-01-15T09:00:00.000000Z"

    def test_handle_success_completed_quiz(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        user_participation = UserParticipationData(
            status="completed",
            invited_at="2024-01-15T10:30:00.000000Z",
            started_at="2024-01-15T11:00:00.000000Z",
            completed_at="2024-01-16T14:20:00.000000Z",
            score=85,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertIsInstance(response, GetUserQuizProgressResponse)
        self.assertEqual(response.quiz_id, str(self.quiz_id))
        self.assertEqual(response.quiz_title, "JavaScript Fundamentals")
        self.assertEqual(response.quiz_description, "Learn the basics of JavaScript")
        self.assertEqual(response.total_questions, 10)
        self.assertEqual(response.total_possible_points, 100)
        self.assertEqual(response.quiz_created_at, "2024-01-15T09:00:00.000000Z")
        self.assertEqual(response.participation.status, "completed")
        self.assertEqual(response.participation.invited_at, "2024-01-15T10:30:00.000000Z")
        self.assertEqual(response.participation.completed_at, "2024-01-16T14:20:00.000000Z")
        self.assertEqual(response.participation.score, 85)
        self.assertEqual(response.participation.score_percentage, 85.0)

        self.mock_quiz_repository.find_or_fail_by_id.assert_called_once_with(quiz_id=self.quiz_id)
        self.mock_participation_finder.find_user_participation_for_quiz.assert_called_once_with(
            quiz_id=self.quiz_id, user_id=self.user_id
        )

    def test_handle_success_invited_quiz(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        user_participation = UserParticipationData(
            status="invited",
            invited_at="2024-01-20T11:00:00.000000Z",
            started_at=None,
            completed_at=None,
            score=None,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertEqual(response.participation.status, "invited")
        self.assertEqual(response.participation.completed_at, None)
        self.assertEqual(response.participation.score, None)
        self.assertEqual(response.participation.score_percentage, None)

    def test_handle_success_perfect_score(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        user_participation = UserParticipationData(
            status="completed",
            invited_at="2024-02-01T08:00:00.000000Z",
            started_at="2024-02-01T08:30:00.000000Z",
            completed_at="2024-02-01T09:30:00.000000Z",
            score=100,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertEqual(response.participation.score, 100)
        self.assertEqual(response.participation.score_percentage, 100.0)

    def test_handle_success_zero_score(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        user_participation = UserParticipationData(
            status="completed",
            invited_at="2024-02-05T14:00:00.000000Z",
            started_at="2024-02-05T14:30:00.000000Z",
            completed_at="2024-02-05T15:45:00.000000Z",
            score=0,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertEqual(response.participation.score, 0)
        self.assertEqual(response.participation.score_percentage, 0.0)

    def test_handle_success_decimal_score_percentage(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        mock_quiz_with_150_points = Mock(spec=Quiz)
        mock_quiz_with_150_points.id = self.quiz_id
        mock_quiz_with_150_points.title = "Advanced Quiz"
        mock_quiz_with_150_points.description = "Advanced concepts quiz"
        mock_quiz_with_150_points.total_questions = 15
        mock_quiz_with_150_points.total_possible_points = 150
        mock_quiz_with_150_points.get_formatted_created_at.return_value = "2024-03-01T12:00:00.000000Z"

        user_participation = UserParticipationData(
            status="completed",
            invited_at="2024-03-01T13:00:00.000000Z",
            started_at="2024-03-01T13:30:00.000000Z",
            completed_at="2024-03-01T14:45:00.000000Z",
            score=125,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = mock_quiz_with_150_points
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertEqual(response.participation.score_percentage, 83.33)

    def test_handle_quiz_not_found_exception(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        self.mock_quiz_repository.find_or_fail_by_id.side_effect = QuizNotFoundException(str(self.quiz_id))

        with self.assertRaises(QuizNotFoundException):
            self.handler.handle(query)

    def test_handle_participation_not_found_exception(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = None

        with self.assertRaises(ParticipationNotFoundForUserException) as context:
            self.handler.handle(query)

        self.assertEqual(context.exception.quiz_id, str(self.quiz_id))
        self.assertEqual(context.exception.user_id, str(self.user_id))

    def test_handle_quiz_with_zero_total_points(self):
        query = GetUserQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.user_id),
        )

        mock_zero_points_quiz = Mock(spec=Quiz)
        mock_zero_points_quiz.id = self.quiz_id
        mock_zero_points_quiz.title = "Zero Points Quiz"
        mock_zero_points_quiz.description = "A quiz with no points"
        mock_zero_points_quiz.total_questions = 5
        mock_zero_points_quiz.total_possible_points = 0
        mock_zero_points_quiz.get_formatted_created_at.return_value = "2024-04-01T10:00:00.000000Z"

        user_participation = UserParticipationData(
            status="completed",
            invited_at="2024-04-01T11:00:00.000000Z",
            started_at="2024-04-01T11:30:00.000000Z",
            completed_at="2024-04-01T12:00:00.000000Z",
            score=0,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = mock_zero_points_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertEqual(response.participation.score_percentage, None)

    def test_handle_with_different_quiz_and_user_ids(self):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")

        query = GetUserQuizProgressQuery(
            quiz_id=str(different_quiz_id),
            requester_id=str(different_user_id),
        )

        different_quiz = Mock(spec=Quiz)
        different_quiz.id = different_quiz_id
        different_quiz.title = "Different Quiz"
        different_quiz.description = "A different quiz"
        different_quiz.total_questions = 8
        different_quiz.total_possible_points = 80
        different_quiz.get_formatted_created_at.return_value = "2024-05-01T15:00:00.000000Z"

        user_participation = UserParticipationData(
            status="completed",
            invited_at="2024-05-01T16:00:00.000000Z",
            started_at="2024-05-01T16:30:00.000000Z",
            completed_at="2024-05-01T17:00:00.000000Z",
            score=72,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = different_quiz
        self.mock_participation_finder.find_user_participation_for_quiz.return_value = user_participation

        response = self.handler.handle(query)

        self.assertEqual(response.quiz_id, str(different_quiz_id))
        self.mock_quiz_repository.find_or_fail_by_id.assert_called_once_with(quiz_id=different_quiz_id)
        self.mock_participation_finder.find_user_participation_for_quiz.assert_called_once_with(
            quiz_id=different_quiz_id, user_id=different_user_id
        )
