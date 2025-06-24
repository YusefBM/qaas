import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.application.get_quiz_scores.get_quiz_scores_query import GetQuizScoresQuery
from quiz.application.get_quiz_scores.get_quiz_scores_query_handler import GetQuizScoresQueryHandler
from quiz.application.get_quiz_scores.get_quiz_scores_response import GetQuizScoresResponse
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.quiz_repository import QuizRepository
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class TestGetQuizScoresQueryHandler(unittest.TestCase):
    def setUp(self):
        self.quiz_repository_mock = Mock(spec=QuizRepository)
        self.participation_finder_mock = Mock(spec=ParticipationFinder)

        self.handler = GetQuizScoresQueryHandler(
            quiz_repository=self.quiz_repository_mock, participation_finder=self.participation_finder_mock
        )

        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.creator_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.unauthorized_user_id = UUID("11111111-2222-3333-4444-555555555555")

        self.query = GetQuizScoresQuery(quiz_id=str(self.quiz_id), requester_id=str(self.creator_id))

    def test_handle_success_with_participants(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "JavaScript Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 15
        mock_quiz_scores_summary.average_score = 78.5
        mock_quiz_scores_summary.max_score = 95
        mock_quiz_scores_summary.min_score = 45
        mock_quiz_scores_summary.top_scorer_email = "best@student.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "JavaScript Quiz")
        self.assertEqual(result.total_participants, 15)
        self.assertEqual(result.average_score, 78.5)
        self.assertEqual(result.max_score, 95)
        self.assertEqual(result.min_score, 45)
        self.assertEqual(result.top_scorer_email, "best@student.com")

        self.quiz_repository_mock.find_or_fail_by_id.assert_called_once_with(
            quiz_id=UUID("12345678-1234-5678-9abc-123456789abc")
        )
        self.participation_finder_mock.find_quiz_scores_summary.assert_called_once_with(
            quiz_id=UUID("12345678-1234-5678-9abc-123456789abc")
        )

    def test_handle_success_with_no_participants(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Empty Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 0
        mock_quiz_scores_summary.average_score = 0
        mock_quiz_scores_summary.max_score = 0
        mock_quiz_scores_summary.min_score = 0
        mock_quiz_scores_summary.top_scorer_email = None

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Empty Quiz")
        self.assertEqual(result.total_participants, 0)
        self.assertEqual(result.average_score, 0)
        self.assertEqual(result.max_score, 0)
        self.assertEqual(result.min_score, 0)
        self.assertIsNone(result.top_scorer_email)

    def test_handle_quiz_not_found_raises_exception(self):
        self.quiz_repository_mock.find_or_fail_by_id.side_effect = QuizNotFoundException(
            "12345678-1234-5678-9abc-123456789abc"
        )

        with self.assertRaises(QuizNotFoundException):
            self.handler.handle(self.query)

        self.participation_finder_mock.find_quiz_scores_summary.assert_not_called()

    def test_handle_unauthorized_access_raises_exception(self):
        unauthorized_query = GetQuizScoresQuery(quiz_id=str(self.quiz_id), requester_id=str(self.unauthorized_user_id))

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.creator_id = self.creator_id

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz

        with self.assertRaises(UnauthorizedQuizAccessException) as context:
            self.handler.handle(unauthorized_query)

        self.assertEqual(context.exception.quiz_id, "12345678-1234-5678-9abc-123456789abc")
        self.assertEqual(context.exception.user_id, "11111111-2222-3333-4444-555555555555")

        self.participation_finder_mock.find_quiz_scores_summary.assert_not_called()

    def test_handle_perfect_scores(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Perfect Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 3
        mock_quiz_scores_summary.average_score = 100.0
        mock_quiz_scores_summary.max_score = 100
        mock_quiz_scores_summary.min_score = 100
        mock_quiz_scores_summary.top_scorer_email = "perfect@student.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Perfect Quiz")
        self.assertEqual(result.total_participants, 3)
        self.assertEqual(result.average_score, 100.0)
        self.assertEqual(result.max_score, 100)
        self.assertEqual(result.min_score, 100)
        self.assertEqual(result.top_scorer_email, "perfect@student.com")

    def test_handle_low_scores(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Difficult Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 8
        mock_quiz_scores_summary.average_score = 25.5
        mock_quiz_scores_summary.max_score = 60
        mock_quiz_scores_summary.min_score = 0
        mock_quiz_scores_summary.top_scorer_email = "survivor@student.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Difficult Quiz")
        self.assertEqual(result.total_participants, 8)
        self.assertEqual(result.average_score, 25.5)
        self.assertEqual(result.max_score, 60)
        self.assertEqual(result.min_score, 0)
        self.assertEqual(result.top_scorer_email, "survivor@student.com")

    def test_handle_single_participant(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Solo Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 1
        mock_quiz_scores_summary.average_score = 85.0
        mock_quiz_scores_summary.max_score = 85
        mock_quiz_scores_summary.min_score = 85
        mock_quiz_scores_summary.top_scorer_email = "only@student.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Solo Quiz")
        self.assertEqual(result.total_participants, 1)
        self.assertEqual(result.average_score, 85.0)
        self.assertEqual(result.max_score, 85)
        self.assertEqual(result.min_score, 85)
        self.assertEqual(result.top_scorer_email, "only@student.com")

    def test_handle_different_quiz_id(self):
        different_quiz_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        different_query = GetQuizScoresQuery(quiz_id=str(different_quiz_id), requester_id=str(self.creator_id))

        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = different_quiz_id
        mock_quiz.title = "Different Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 5
        mock_quiz_scores_summary.average_score = 90.0
        mock_quiz_scores_summary.max_score = 100
        mock_quiz_scores_summary.min_score = 75
        mock_quiz_scores_summary.top_scorer_email = "ace@student.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(different_query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, different_quiz_id)
        self.assertEqual(result.quiz_title, "Different Quiz")
        self.assertEqual(result.total_participants, 5)
        self.assertEqual(result.average_score, 90.0)
        self.assertEqual(result.max_score, 100)
        self.assertEqual(result.min_score, 75)
        self.assertEqual(result.top_scorer_email, "ace@student.com")

        self.quiz_repository_mock.find_or_fail_by_id.assert_called_once_with(
            quiz_id=UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        )
        self.participation_finder_mock.find_quiz_scores_summary.assert_called_once_with(
            quiz_id=UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        )

    def test_handle_authorization_check_with_string_ids(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Authorization Test Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 2
        mock_quiz_scores_summary.average_score = 75.0
        mock_quiz_scores_summary.max_score = 90
        mock_quiz_scores_summary.min_score = 60
        mock_quiz_scores_summary.top_scorer_email = "auth@test.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Authorization Test Quiz")
        self.assertEqual(result.total_participants, 2)

    def test_handle_fractional_average_score(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id
        mock_quiz.title = "Fractional Quiz"
        mock_quiz.creator_id = self.creator_id

        mock_quiz_scores_summary = Mock(spec=QuizScoresSummary)
        mock_quiz_scores_summary.total_participants = 7
        mock_quiz_scores_summary.average_score = 67.85714285714286
        mock_quiz_scores_summary.max_score = 92
        mock_quiz_scores_summary.min_score = 43
        mock_quiz_scores_summary.top_scorer_email = "math@student.com"

        self.quiz_repository_mock.find_or_fail_by_id.return_value = mock_quiz
        self.participation_finder_mock.find_quiz_scores_summary.return_value = mock_quiz_scores_summary

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetQuizScoresResponse)
        self.assertEqual(result.quiz_id, self.quiz_id)
        self.assertEqual(result.quiz_title, "Fractional Quiz")
        self.assertEqual(result.total_participants, 7)
        self.assertEqual(result.average_score, 67.85714285714286)
        self.assertEqual(result.max_score, 92)
        self.assertEqual(result.min_score, 43)
        self.assertEqual(result.top_scorer_email, "math@student.com")
