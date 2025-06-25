import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.quiz_progress_summary import QuizProgressSummary
from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary
from quiz.domain.participation.user_participation_data import UserParticipationData
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

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_user_participation_for_quiz_success_completed(self, mock_objects):
        user_id = UUID("87654321-4321-8765-cba9-987654321098")

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.get_formatted_invited_at.return_value = "2024-01-15T10:30:00.000000Z"

        mock_participation = Mock(spec=Participation)
        mock_participation.status.value = "completed"
        mock_participation.invitation = mock_invitation
        mock_participation.score = 85
        mock_participation.get_formatted_created_at.return_value = "2024-01-15T11:00:00.000000Z"
        mock_participation.get_formatted_completed_at.return_value = "2024-01-16T14:20:00.000000Z"

        mock_objects.select_related.return_value.get.return_value = mock_participation

        result = self.finder.find_user_participation_for_quiz(self.quiz_id, user_id)

        self.assertIsInstance(result, UserParticipationData)
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.invited_at, "2024-01-15T10:30:00.000000Z")
        self.assertEqual(result.started_at, "2024-01-15T11:00:00.000000Z")
        self.assertEqual(result.completed_at, "2024-01-16T14:20:00.000000Z")
        self.assertEqual(result.score, 85)

        mock_objects.select_related.assert_called_once_with("invitation")
        mock_objects.select_related.return_value.get.assert_called_once_with(
            quiz_id=self.quiz_id, participant_id=user_id
        )

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_user_participation_for_quiz_success_invited_no_invitation(self, mock_objects):
        user_id = UUID("87654321-4321-8765-cba9-987654321098")

        mock_participation = Mock(spec=Participation)
        mock_participation.status.value = "invited"
        mock_participation.invitation = None
        mock_participation.score = None
        mock_participation.get_formatted_created_at.return_value = "2024-01-20T11:00:00.000000Z"
        mock_participation.get_formatted_completed_at.return_value = None

        mock_objects.select_related.return_value.get.return_value = mock_participation

        result = self.finder.find_user_participation_for_quiz(self.quiz_id, user_id)

        self.assertIsInstance(result, UserParticipationData)
        self.assertEqual(result.status, "invited")
        self.assertEqual(result.invited_at, None)
        self.assertEqual(result.started_at, "2024-01-20T11:00:00.000000Z")
        self.assertEqual(result.completed_at, None)
        self.assertEqual(result.score, None)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_user_participation_for_quiz_not_found(self, mock_objects):
        user_id = UUID("87654321-4321-8765-cba9-987654321098")

        mock_objects.select_related.return_value.get.side_effect = Participation.DoesNotExist

        result = self.finder.find_user_participation_for_quiz(self.quiz_id, user_id)

        self.assertIsNone(result)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_user_participation_for_quiz_different_ids(self, mock_objects):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")

        mock_participation = Mock(spec=Participation)
        mock_participation.status.value = "in_progress"
        mock_participation.invitation = None
        mock_participation.score = None
        mock_participation.get_formatted_created_at.return_value = "2024-03-01T10:00:00.000000Z"
        mock_participation.get_formatted_completed_at.return_value = None

        mock_objects.select_related.return_value.get.return_value = mock_participation

        result = self.finder.find_user_participation_for_quiz(different_quiz_id, different_user_id)

        self.assertIsInstance(result, UserParticipationData)
        self.assertEqual(result.status, "in_progress")

        mock_objects.select_related.return_value.get.assert_called_once_with(
            quiz_id=different_quiz_id, participant_id=different_user_id
        )

    @patch("quiz.domain.participation.participation.Participation.objects")
    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_creator_quiz_progress_summary_active_quiz(self, mock_invitation_objects, mock_participation_objects):
        mock_invitation_stats = {
            "total_sent": 10,
            "total_accepted": 8,
        }

        mock_participation_stats = {
            "total_participants": 8,
            "completed_participants": 6,
        }

        mock_invitation_objects.filter.return_value.aggregate.return_value = mock_invitation_stats
        mock_participation_objects.filter.return_value.aggregate.return_value = mock_participation_stats

        result = self.finder.find_creator_quiz_progress_summary(self.quiz_id)

        self.assertIsInstance(result, QuizProgressSummary)

        self.assertEqual(result.invitation_stats.total_sent, 10)
        self.assertEqual(result.invitation_stats.total_accepted, 8)
        self.assertEqual(result.invitation_stats.acceptance_rate, 80.0)
        self.assertEqual(result.invitation_stats.pending_invitations, 2)

        self.assertEqual(result.participation_stats.total_participants, 8)
        self.assertEqual(result.participation_stats.completed_participants, 6)
        self.assertEqual(result.participation_stats.completion_rate, 75.0)

        mock_invitation_objects.filter.assert_called_once_with(quiz_id=self.quiz_id)
        mock_participation_objects.filter.assert_called_once_with(quiz_id=self.quiz_id)

    @patch("quiz.domain.participation.participation.Participation.objects")
    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_creator_quiz_progress_summary_new_quiz_no_invitations(
        self, mock_invitation_objects, mock_participation_objects
    ):
        mock_invitation_stats = {
            "total_sent": 0,
            "total_accepted": 0,
        }

        mock_participation_stats = {
            "total_participants": 0,
            "completed_participants": 0,
        }

        mock_invitation_objects.filter.return_value.aggregate.return_value = mock_invitation_stats
        mock_participation_objects.filter.return_value.aggregate.return_value = mock_participation_stats

        result = self.finder.find_creator_quiz_progress_summary(self.quiz_id)

        self.assertIsInstance(result, QuizProgressSummary)

        self.assertEqual(result.invitation_stats.total_sent, 0)
        self.assertEqual(result.invitation_stats.total_accepted, 0)
        self.assertEqual(result.invitation_stats.acceptance_rate, 0.0)
        self.assertEqual(result.invitation_stats.pending_invitations, 0)

        self.assertEqual(result.participation_stats.total_participants, 0)
        self.assertEqual(result.participation_stats.completed_participants, 0)
        self.assertEqual(result.participation_stats.completion_rate, 0.0)

    @patch("quiz.domain.participation.participation.Participation.objects")
    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_creator_quiz_progress_summary_perfect_rates(
        self, mock_invitation_objects, mock_participation_objects
    ):
        mock_invitation_stats = {
            "total_sent": 5,
            "total_accepted": 5,
        }

        mock_participation_stats = {
            "total_participants": 5,
            "completed_participants": 5,
        }

        mock_invitation_objects.filter.return_value.aggregate.return_value = mock_invitation_stats
        mock_participation_objects.filter.return_value.aggregate.return_value = mock_participation_stats

        result = self.finder.find_creator_quiz_progress_summary(self.quiz_id)

        self.assertEqual(result.invitation_stats.acceptance_rate, 100.0)
        self.assertEqual(result.participation_stats.completion_rate, 100.0)

    @patch("quiz.domain.participation.participation.Participation.objects")
    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_creator_quiz_progress_summary_low_engagement(
        self, mock_invitation_objects, mock_participation_objects
    ):
        mock_invitation_stats = {
            "total_sent": 20,
            "total_accepted": 3,
        }

        mock_participation_stats = {
            "total_participants": 3,
            "completed_participants": 1,
        }

        mock_invitation_objects.filter.return_value.aggregate.return_value = mock_invitation_stats
        mock_participation_objects.filter.return_value.aggregate.return_value = mock_participation_stats

        result = self.finder.find_creator_quiz_progress_summary(self.quiz_id)

        self.assertEqual(result.invitation_stats.acceptance_rate, 15.0)
        self.assertEqual(result.invitation_stats.pending_invitations, 17)
        self.assertEqual(result.participation_stats.completion_rate, 33.33)

    @patch("quiz.domain.participation.participation.Participation.objects")
    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_creator_quiz_progress_summary_with_different_quiz_id(
        self, mock_invitation_objects, mock_participation_objects
    ):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")

        mock_invitation_stats = {
            "total_sent": 15,
            "total_accepted": 12,
        }

        mock_participation_stats = {
            "total_participants": 12,
            "completed_participants": 10,
        }

        mock_invitation_objects.filter.return_value.aggregate.return_value = mock_invitation_stats
        mock_participation_objects.filter.return_value.aggregate.return_value = mock_participation_stats

        result = self.finder.find_creator_quiz_progress_summary(different_quiz_id)

        self.assertEqual(result.invitation_stats.total_sent, 15)
        self.assertEqual(result.invitation_stats.total_accepted, 12)
        self.assertEqual(result.participation_stats.total_participants, 12)
        self.assertEqual(result.participation_stats.completed_participants, 10)

        mock_invitation_objects.filter.assert_called_once_with(quiz_id=different_quiz_id)
        mock_participation_objects.filter.assert_called_once_with(quiz_id=different_quiz_id)

    @patch("quiz.domain.participation.participation.Participation.objects")
    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_creator_quiz_progress_summary_partial_acceptance_partial_completion(
        self, mock_invitation_objects, mock_participation_objects
    ):
        mock_invitation_stats = {
            "total_sent": 13,
            "total_accepted": 7,
        }

        mock_participation_stats = {
            "total_participants": 7,
            "completed_participants": 5,
        }

        mock_invitation_objects.filter.return_value.aggregate.return_value = mock_invitation_stats
        mock_participation_objects.filter.return_value.aggregate.return_value = mock_participation_stats

        result = self.finder.find_creator_quiz_progress_summary(self.quiz_id)

        self.assertEqual(result.invitation_stats.acceptance_rate, 53.85)
        self.assertEqual(result.invitation_stats.pending_invitations, 6)
        self.assertEqual(result.participation_stats.completion_rate, 71.43)
