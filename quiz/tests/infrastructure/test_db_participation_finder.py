import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.domain.participation.participation import Participation
from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary
from quiz.infrastructure.db_participation_finder import DbParticipationFinder
from user.domain.user import User


class TestDbParticipationFinder(unittest.TestCase):
    def setUp(self):
        self.finder = DbParticipationFinder()
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_with_participants_and_scores(self, mock_objects):
        mock_stats_data = {
            "total_participants": 5,
            "average_score": 78.5,
            "max_score": 95.0,
            "min_score": 45.0,
        }

        mock_top_scorer_participation = Mock(spec=Participation)
        mock_participant = Mock(spec=User)
        mock_participant.email = "top@student.com"
        mock_top_scorer_participation.participant = mock_participant

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = (
            mock_top_scorer_participation
        )

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(self.quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 5)
        self.assertEqual(result.average_score, 78.5)
        self.assertEqual(result.max_score, 95.0)
        self.assertEqual(result.min_score, 45.0)
        self.assertEqual(result.top_scorer_email, "top@student.com")

        self.assertEqual(mock_objects.filter.call_count, 2)
        mock_objects.filter.assert_any_call(quiz_id=self.quiz_id)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_with_no_participants(self, mock_objects):
        mock_stats_data = {
            "total_participants": 0,
            "average_score": 0.0,
            "max_score": 0.0,
            "min_score": 0.0,
        }

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = None

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(self.quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 0)
        self.assertEqual(result.average_score, 0.0)
        self.assertEqual(result.max_score, 0.0)
        self.assertEqual(result.min_score, 0.0)
        self.assertIsNone(result.top_scorer_email)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_with_single_participant(self, mock_objects):
        mock_stats_data = {
            "total_participants": 1,
            "average_score": 87.3,
            "max_score": 87.3,
            "min_score": 87.3,
        }

        mock_top_scorer_participation = Mock(spec=Participation)
        mock_participant = Mock(spec=User)
        mock_participant.email = "solo@student.com"
        mock_top_scorer_participation.participant = mock_participant

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = (
            mock_top_scorer_participation
        )

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(self.quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 1)
        self.assertEqual(result.average_score, 87.3)
        self.assertEqual(result.max_score, 87.3)
        self.assertEqual(result.min_score, 87.3)
        self.assertEqual(result.top_scorer_email, "solo@student.com")

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_with_perfect_scores(self, mock_objects):
        mock_stats_data = {
            "total_participants": 3,
            "average_score": 100.0,
            "max_score": 100.0,
            "min_score": 100.0,
        }

        mock_top_scorer_participation = Mock(spec=Participation)
        mock_participant = Mock(spec=User)
        mock_participant.email = "perfect@student.com"
        mock_top_scorer_participation.participant = mock_participant

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = (
            mock_top_scorer_participation
        )

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(self.quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 3)
        self.assertEqual(result.average_score, 100.0)
        self.assertEqual(result.max_score, 100.0)
        self.assertEqual(result.min_score, 100.0)
        self.assertEqual(result.top_scorer_email, "perfect@student.com")

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_rounds_fractional_scores(self, mock_objects):
        mock_stats_data = {
            "total_participants": 7,
            "average_score": 67.85714285714286,
            "max_score": 95.666666666666,
            "min_score": 33.33333333333333,
        }

        mock_top_scorer_participation = Mock(spec=Participation)
        mock_participant = Mock(spec=User)
        mock_participant.email = "math@student.com"
        mock_top_scorer_participation.participant = mock_participant

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = (
            mock_top_scorer_participation
        )

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(self.quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 7)
        self.assertEqual(result.average_score, 67.86)
        self.assertEqual(result.max_score, 95.67)
        self.assertEqual(result.min_score, 33.33)
        self.assertEqual(result.top_scorer_email, "math@student.com")

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_with_participants_but_no_completed_scores(self, mock_objects):
        mock_stats_data = {
            "total_participants": 3,
            "average_score": 0.0,
            "max_score": 0.0,
            "min_score": 0.0,
        }

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = None

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(self.quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 3)
        self.assertEqual(result.average_score, 0.0)
        self.assertEqual(result.max_score, 0.0)
        self.assertEqual(result.min_score, 0.0)
        self.assertIsNone(result.top_scorer_email)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_quiz_scores_summary_different_quiz_id(self, mock_objects):
        different_quiz_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        mock_stats_data = {
            "total_participants": 2,
            "average_score": 90.5,
            "max_score": 98.0,
            "min_score": 83.0,
        }

        mock_top_scorer_participation = Mock(spec=Participation)
        mock_participant = Mock(spec=User)
        mock_participant.email = "different@student.com"
        mock_top_scorer_participation.participant = mock_participant

        mock_filter_queryset = Mock()
        mock_filter_queryset.aggregate.return_value = mock_stats_data
        mock_filter_queryset.select_related.return_value.order_by.return_value.first.return_value = (
            mock_top_scorer_participation
        )

        mock_objects.filter.return_value = mock_filter_queryset

        result = self.finder.find_quiz_scores_summary(different_quiz_id)

        self.assertIsInstance(result, QuizScoresSummary)
        self.assertEqual(result.total_participants, 2)
        self.assertEqual(result.average_score, 90.5)
        self.assertEqual(result.max_score, 98.0)
        self.assertEqual(result.min_score, 83.0)
        self.assertEqual(result.top_scorer_email, "different@student.com")

        self.assertEqual(mock_objects.filter.call_count, 2)
        mock_objects.filter.assert_any_call(quiz_id=different_quiz_id)
