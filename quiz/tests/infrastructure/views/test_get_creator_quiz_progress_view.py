import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status

from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_response import (
    GetCreatorQuizProgressResponse,
    InvitationStats,
    ParticipationStats,
)
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException
from quiz.infrastructure.views.get_creator_quiz_progress_view import GetCreatorQuizProgressView
from user.domain.user import User


class TestGetCreatorQuizProgressView(unittest.TestCase):
    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user

        self.mock_query_handler = Mock()
        self.mock_logger = Mock()
        self.view = GetCreatorQuizProgressView(query_handler=self.mock_query_handler, logger=self.mock_logger)

    def test_get_success_active_quiz(self):
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

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="JavaScript Fundamentals",
            quiz_description="Learn the basics of JavaScript",
            total_questions=10,
            created_at="2024-01-15T09:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(self.quiz_id))
        self.assertEqual(response.data["quiz_title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["quiz_description"], "Learn the basics of JavaScript")
        self.assertEqual(response.data["total_questions"], 10)
        self.assertEqual(response.data["created_at"], "2024-01-15T09:00:00.000000Z")

        self.assertEqual(response.data["invitation_stats"]["total_sent"], 10)
        self.assertEqual(response.data["invitation_stats"]["total_accepted"], 8)
        self.assertEqual(response.data["invitation_stats"]["acceptance_rate"], 80.0)
        self.assertEqual(response.data["invitation_stats"]["pending_invitations"], 2)

        self.assertEqual(response.data["participation_stats"]["total_participants"], 8)
        self.assertEqual(response.data["participation_stats"]["completed_participants"], 6)
        self.assertEqual(response.data["participation_stats"]["completion_rate"], 75.0)

        self.mock_query_handler.handle.assert_called_once()
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.quiz_id, str(self.quiz_id))
        self.assertEqual(query_arg.requester_id, str(self.user_id))

    def test_get_success_new_quiz_no_invitations(self):
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

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="New Quiz",
            quiz_description="A newly created quiz",
            total_questions=5,
            created_at="2024-02-01T10:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_title"], "New Quiz")
        self.assertEqual(response.data["invitation_stats"]["total_sent"], 0)
        self.assertEqual(response.data["invitation_stats"]["acceptance_rate"], 0.0)
        self.assertEqual(response.data["participation_stats"]["total_participants"], 0)
        self.assertEqual(response.data["participation_stats"]["completion_rate"], 0.0)

    def test_get_success_perfect_rates(self):
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

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Popular Quiz",
            quiz_description="A highly engaging quiz",
            total_questions=15,
            created_at="2024-02-05T14:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invitation_stats"]["acceptance_rate"], 100.0)
        self.assertEqual(response.data["participation_stats"]["completion_rate"], 100.0)

    def test_get_success_low_engagement(self):
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

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Challenging Quiz",
            quiz_description="A difficult quiz that few complete",
            total_questions=25,
            created_at="2024-02-10T08:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invitation_stats"]["acceptance_rate"], 15.0)
        self.assertEqual(response.data["invitation_stats"]["pending_invitations"], 17)
        self.assertEqual(response.data["participation_stats"]["completion_rate"], 33.33)

    def test_get_success_single_participant(self):
        invitation_stats = InvitationStats(
            total_sent=1,
            total_accepted=1,
            acceptance_rate=100.0,
            pending_invitations=0,
        )

        participation_stats = ParticipationStats(
            total_participants=1,
            completed_participants=1,
            completion_rate=100.0,
        )

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Personal Quiz",
            quiz_description="A quiz for a single participant",
            total_questions=8,
            created_at="2024-02-15T16:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invitation_stats"]["total_sent"], 1)
        self.assertEqual(response.data["participation_stats"]["total_participants"], 1)

    def test_get_handles_quiz_not_found_exception(self):
        self.mock_query_handler.handle.side_effect = QuizNotFoundException(str(self.quiz_id))

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Quiz with ID '12345678-1234-5678-9abc-123456789abc' not found", response.data["message"])

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
        self.assertEqual(response.data["message"], "Internal server error when getting creator quiz progress")

    def test_get_with_different_quiz_id(self):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")

        invitation_stats = InvitationStats(
            total_sent=15,
            total_accepted=12,
            acceptance_rate=80.0,
            pending_invitations=3,
        )

        participation_stats = ParticipationStats(
            total_participants=12,
            completed_participants=10,
            completion_rate=83.33,
        )

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(different_quiz_id),
            quiz_title="Python Advanced",
            quiz_description="Advanced Python concepts",
            total_questions=20,
            created_at="2024-03-01T11:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
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

        invitation_stats = InvitationStats(
            total_sent=7,
            total_accepted=5,
            acceptance_rate=71.43,
            pending_invitations=2,
        )

        participation_stats = ParticipationStats(
            total_participants=5,
            completed_participants=4,
            completion_rate=80.0,
        )

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="React Components",
            quiz_description="Understanding React components",
            total_questions=12,
            created_at="2024-03-05T13:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(different_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        query_arg = self.mock_query_handler.handle.call_args[0][0]
        self.assertEqual(query_arg.requester_id, str(different_user_id))

    def test_get_with_many_invitations(self):
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

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Popular Programming Quiz",
            quiz_description="A widely distributed programming quiz",
            total_questions=30,
            created_at="2024-03-10T09:00:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invitation_stats"]["total_sent"], 100)
        self.assertEqual(response.data["participation_stats"]["total_participants"], 75)
        self.assertEqual(response.data["participation_stats"]["completed_participants"], 60)

    def test_get_with_partial_completion(self):
        invitation_stats = InvitationStats(
            total_sent=12,
            total_accepted=10,
            acceptance_rate=83.33,
            pending_invitations=2,
        )

        participation_stats = ParticipationStats(
            total_participants=10,
            completed_participants=3,
            completion_rate=30.0,
        )

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Lengthy Quiz",
            quiz_description="A comprehensive quiz that takes time to complete",
            total_questions=50,
            created_at="2024-03-15T07:30:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["participation_stats"]["completion_rate"], 30.0)
        self.assertEqual(response.data["total_questions"], 50)

    def test_get_with_decimal_acceptance_rate(self):
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

        mock_response = GetCreatorQuizProgressResponse(
            quiz_id=str(self.quiz_id),
            quiz_title="Specialized Quiz",
            quiz_description="A quiz targeting specific skills",
            total_questions=18,
            created_at="2024-03-20T12:15:00.000000Z",
            invitation_stats=invitation_stats,
            participation_stats=participation_stats,
        )

        self.mock_query_handler.handle.return_value = mock_response

        response = self.view.get(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invitation_stats"]["acceptance_rate"], 53.85)
        self.assertEqual(response.data["participation_stats"]["completion_rate"], 71.43)
