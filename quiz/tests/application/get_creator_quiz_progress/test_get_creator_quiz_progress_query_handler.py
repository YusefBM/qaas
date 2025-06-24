import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query import GetCreatorQuizProgressQuery
from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_query_handler import (
    GetCreatorQuizProgressQueryHandler,
)
from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_response import (
    GetCreatorQuizProgressResponse,
    InvitationStats,
    ParticipationStats,
)
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.participation.quiz_progress_summary import QuizProgressSummary
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.quiz_repository import QuizRepository
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException
from user.domain.user import User


class TestGetCreatorQuizProgressQueryHandler(unittest.TestCase):

    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.creator_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.other_user_id = UUID("11111111-2222-3333-4444-555555555555")

        self.mock_quiz_repository = Mock(spec=QuizRepository)
        self.mock_participation_finder = Mock(spec=ParticipationFinder)

        self.handler = GetCreatorQuizProgressQueryHandler(
            quiz_repository=self.mock_quiz_repository,
            participation_finder=self.mock_participation_finder,
        )

        self.mock_creator = Mock(spec=User)
        self.mock_creator.id = self.creator_id

        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.id = self.quiz_id
        self.mock_quiz.creator_id = self.creator_id
        self.mock_quiz.title = "JavaScript Fundamentals"
        self.mock_quiz.description = "Learn the basics of JavaScript"
        self.mock_quiz.total_questions = 10
        self.mock_quiz.get_formatted_created_at.return_value = "2024-01-15T09:00:00.000000Z"

    def test_handle_success_active_quiz(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=10,
            total_accepted=8,
            acceptance_rate=80.0,
            pending_invitations=2,
        )

        participation_stats = ParticipationStats(
            total_participants=8,
            completed_participants=6,
            completion_rate=75.0,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertIsInstance(response, GetCreatorQuizProgressResponse)
        self.assertEqual(response.quiz_id, str(self.quiz_id))
        self.assertEqual(response.quiz_title, "JavaScript Fundamentals")
        self.assertEqual(response.quiz_description, "Learn the basics of JavaScript")
        self.assertEqual(response.total_questions, 10)
        self.assertEqual(response.created_at, "2024-01-15T09:00:00.000000Z")
        self.assertEqual(response.invitation_stats.total_sent, 10)
        self.assertEqual(response.invitation_stats.total_accepted, 8)
        self.assertEqual(response.invitation_stats.acceptance_rate, 80.0)
        self.assertEqual(response.invitation_stats.pending_invitations, 2)
        self.assertEqual(response.participation_stats.total_participants, 8)
        self.assertEqual(response.participation_stats.completed_participants, 6)
        self.assertEqual(response.participation_stats.completion_rate, 75.0)

        self.mock_quiz_repository.find_or_fail_by_id.assert_called_once_with(quiz_id=self.quiz_id)
        self.mock_participation_finder.find_creator_quiz_progress_summary.assert_called_once_with(quiz_id=self.quiz_id)

    def test_handle_success_new_quiz_no_invitations(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=0,
            total_accepted=0,
            acceptance_rate=0.0,
            pending_invitations=0,
        )

        participation_stats = ParticipationStats(
            total_participants=0,
            completed_participants=0,
            completion_rate=0.0,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.invitation_stats.total_sent, 0)
        self.assertEqual(response.invitation_stats.acceptance_rate, 0.0)
        self.assertEqual(response.participation_stats.total_participants, 0)
        self.assertEqual(response.participation_stats.completion_rate, 0.0)

    def test_handle_success_perfect_rates(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=5,
            total_accepted=5,
            acceptance_rate=100.0,
            pending_invitations=0,
        )

        participation_stats = ParticipationStats(
            total_participants=5,
            completed_participants=5,
            completion_rate=100.0,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.invitation_stats.acceptance_rate, 100.0)
        self.assertEqual(response.participation_stats.completion_rate, 100.0)

    def test_handle_success_low_engagement(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=20,
            total_accepted=3,
            acceptance_rate=15.0,
            pending_invitations=17,
        )

        participation_stats = ParticipationStats(
            total_participants=3,
            completed_participants=1,
            completion_rate=33.33,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.invitation_stats.acceptance_rate, 15.0)
        self.assertEqual(response.invitation_stats.pending_invitations, 17)
        self.assertEqual(response.participation_stats.completion_rate, 33.33)

    def test_handle_quiz_not_found_exception(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        self.mock_quiz_repository.find_or_fail_by_id.side_effect = QuizNotFoundException(str(self.quiz_id))

        with self.assertRaises(QuizNotFoundException):
            self.handler.handle(query)

    def test_handle_unauthorized_quiz_access_exception(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.other_user_id),
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz

        with self.assertRaises(UnauthorizedQuizAccessException) as context:
            self.handler.handle(query)

        self.assertEqual(context.exception.quiz_id, str(self.quiz_id))
        self.assertEqual(context.exception.user_id, str(self.other_user_id))

    def test_handle_with_different_creator(self):
        different_creator_id = UUID("99999999-8888-7777-6666-555555555555")
        different_quiz_id = UUID("77777777-6666-5555-4444-333333333333")

        query = GetCreatorQuizProgressQuery(
            quiz_id=str(different_quiz_id),
            requester_id=str(different_creator_id),
        )

        different_quiz = Mock(spec=Quiz)
        different_quiz.id = different_quiz_id
        different_quiz.creator_id = different_creator_id
        different_quiz.title = "Python Advanced"
        different_quiz.description = "Advanced Python concepts"
        different_quiz.total_questions = 15
        different_quiz.get_formatted_created_at.return_value = "2024-02-01T12:00:00.000000Z"

        invitation_stats = InvitationStats(
            total_sent=12,
            total_accepted=9,
            acceptance_rate=75.0,
            pending_invitations=3,
        )

        participation_stats = ParticipationStats(
            total_participants=9,
            completed_participants=7,
            completion_rate=77.78,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = different_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.quiz_id, str(different_quiz_id))
        self.assertEqual(response.quiz_title, "Python Advanced")
        self.mock_quiz_repository.find_or_fail_by_id.assert_called_once_with(quiz_id=different_quiz_id)
        self.mock_participation_finder.find_creator_quiz_progress_summary.assert_called_once_with(
            quiz_id=different_quiz_id
        )

    def test_handle_with_many_invitations(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=100,
            total_accepted=75,
            acceptance_rate=75.0,
            pending_invitations=25,
        )

        participation_stats = ParticipationStats(
            total_participants=75,
            completed_participants=60,
            completion_rate=80.0,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.invitation_stats.total_sent, 100)
        self.assertEqual(response.participation_stats.total_participants, 75)
        self.assertEqual(response.participation_stats.completed_participants, 60)

    def test_handle_with_decimal_rates(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=13,
            total_accepted=7,
            acceptance_rate=53.85,
            pending_invitations=6,
        )

        participation_stats = ParticipationStats(
            total_participants=7,
            completed_participants=5,
            completion_rate=71.43,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.invitation_stats.acceptance_rate, 53.85)
        self.assertEqual(response.participation_stats.completion_rate, 71.43)

    def test_handle_with_single_invitation(self):
        query = GetCreatorQuizProgressQuery(
            quiz_id=str(self.quiz_id),
            requester_id=str(self.creator_id),
        )

        invitation_stats = InvitationStats(
            total_sent=1,
            total_accepted=1,
            acceptance_rate=100.0,
            pending_invitations=0,
        )

        participation_stats = ParticipationStats(
            total_participants=1,
            completed_participants=0,
            completion_rate=0.0,
        )

        quiz_progress_summary = QuizProgressSummary(
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_quiz_repository.find_or_fail_by_id.return_value = self.mock_quiz
        self.mock_participation_finder.find_creator_quiz_progress_summary.return_value = quiz_progress_summary

        response = self.handler.handle(query)

        self.assertEqual(response.invitation_stats.total_sent, 1)
        self.assertEqual(response.participation_stats.total_participants, 1)
        self.assertEqual(response.participation_stats.completed_participants, 0)
