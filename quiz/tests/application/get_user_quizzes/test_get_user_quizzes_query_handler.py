import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.application.get_user_quizzes.get_user_quizzes_query import GetUserQuizzesQuery
from quiz.application.get_user_quizzes.get_user_quizzes_query_handler import GetUserQuizzesQueryHandler
from quiz.application.get_user_quizzes.get_user_quizzes_response import GetUserQuizzesResponse, QuizParticipationSummary
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.participation.participation_related_attribute import ParticipationRelatedAttribute
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_repository import QuizRepository


class TestGetUserQuizzesQueryHandler(unittest.TestCase):
    def setUp(self):
        self.quiz_repository_mock = Mock(spec=QuizRepository)
        self.participation_repository_mock = Mock(spec=ParticipationRepository)

        self.handler = GetUserQuizzesQueryHandler(
            quiz_repository=self.quiz_repository_mock, participation_repository=self.participation_repository_mock
        )

        self.user_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.quiz_id_1 = UUID("87654321-4321-8765-cba9-987654321098")
        self.quiz_id_2 = UUID("11111111-2222-3333-4444-555555555555")

        self.query = GetUserQuizzesQuery(requester_id=self.user_id)

    def test_handle_success_with_multiple_participations(self):
        mock_quiz_1 = Mock(spec=Quiz)
        mock_quiz_1.id = self.quiz_id_1
        mock_quiz_1.title = "JavaScript Fundamentals"
        mock_quiz_1.description = "Learn JavaScript basics"
        mock_quiz_1.total_questions = 10
        mock_quiz_1.total_participants = 25
        mock_quiz_1.get_formatted_created_at.return_value = "2024-01-01T12:00:00Z"

        mock_quiz_2 = Mock(spec=Quiz)
        mock_quiz_2.id = self.quiz_id_2
        mock_quiz_2.title = "Python Advanced"
        mock_quiz_2.description = "Advanced Python concepts"
        mock_quiz_2.total_questions = 15
        mock_quiz_2.total_participants = 30
        mock_quiz_2.get_formatted_created_at.return_value = "2024-01-05T14:30:00Z"

        mock_participation_1 = Mock(spec=Participation)
        mock_participation_1.quiz = mock_quiz_1
        mock_participation_1.score = 85
        mock_participation_1.status = "completed"
        mock_participation_1.get_formatted_completed_at.return_value = "2024-01-02T10:15:00Z"
        mock_participation_1.get_formatted_created_at.return_value = "2024-01-01T13:00:00Z"

        mock_participation_2 = Mock(spec=Participation)
        mock_participation_2.quiz = mock_quiz_2
        mock_participation_2.score = None
        mock_participation_2.status = "invited"
        mock_participation_2.get_formatted_completed_at.return_value = None
        mock_participation_2.get_formatted_created_at.return_value = "2024-01-05T15:00:00Z"

        self.participation_repository_mock.find_all_by_user_id.return_value = [
            mock_participation_1,
            mock_participation_2,
        ]

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetUserQuizzesResponse)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result.quizzes_participations), 2)

        participation_1 = result.quizzes_participations[0]
        self.assertEqual(participation_1.quiz_id, self.quiz_id_1)
        self.assertEqual(participation_1.quiz_title, "JavaScript Fundamentals")
        self.assertEqual(participation_1.quiz_description, "Learn JavaScript basics")
        self.assertEqual(participation_1.total_questions, 10)
        self.assertEqual(participation_1.total_participants, 25)
        self.assertEqual(participation_1.score, 85)
        self.assertEqual(participation_1.participation_status, "completed")
        self.assertEqual(participation_1.completed_at, "2024-01-02T10:15:00Z")
        self.assertEqual(participation_1.participation_created_at, "2024-01-01T13:00:00Z")
        self.assertEqual(participation_1.quiz_created_at, "2024-01-01T12:00:00Z")

        participation_2 = result.quizzes_participations[1]
        self.assertEqual(participation_2.quiz_id, self.quiz_id_2)
        self.assertEqual(participation_2.quiz_title, "Python Advanced")
        self.assertEqual(participation_2.quiz_description, "Advanced Python concepts")
        self.assertEqual(participation_2.total_questions, 15)
        self.assertEqual(participation_2.total_participants, 30)
        self.assertIsNone(participation_2.score)
        self.assertEqual(participation_2.participation_status, "invited")
        self.assertIsNone(participation_2.completed_at)
        self.assertEqual(participation_2.participation_created_at, "2024-01-05T15:00:00Z")

        self.participation_repository_mock.find_all_by_user_id.assert_called_once_with(
            user_id=self.user_id, related_attributes=[ParticipationRelatedAttribute.QUIZ]
        )

    def test_handle_success_with_single_participation(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id_1
        mock_quiz.title = "Single Quiz"
        mock_quiz.description = "Only quiz"
        mock_quiz.total_questions = 5
        mock_quiz.total_participants = 1
        mock_quiz.get_formatted_created_at.return_value = "2024-01-01T12:00:00Z"

        mock_participation = Mock(spec=Participation)
        mock_participation.quiz = mock_quiz
        mock_participation.score = 100
        mock_participation.status = "completed"
        mock_participation.get_formatted_completed_at.return_value = "2024-01-01T13:00:00Z"
        mock_participation.get_formatted_created_at.return_value = "2024-01-01T12:30:00Z"

        self.participation_repository_mock.find_all_by_user_id.return_value = [mock_participation]

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetUserQuizzesResponse)
        self.assertEqual(result.total_count, 1)
        self.assertEqual(len(result.quizzes_participations), 1)
        self.assertEqual(result.quizzes_participations[0].quiz_title, "Single Quiz")
        self.assertEqual(result.quizzes_participations[0].score, 100)
        self.assertEqual(result.quizzes_participations[0].participation_status, "completed")

    def test_handle_success_with_empty_participations(self):
        self.participation_repository_mock.find_all_by_user_id.return_value = []

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetUserQuizzesResponse)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.quizzes_participations), 0)

        self.participation_repository_mock.find_all_by_user_id.assert_called_once_with(
            user_id=self.user_id, related_attributes=[ParticipationRelatedAttribute.QUIZ]
        )

    def test_handle_success_with_participation_no_completion_date(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id_1
        mock_quiz.title = "Incomplete Quiz"
        mock_quiz.description = "Not finished yet"
        mock_quiz.total_questions = 8
        mock_quiz.total_participants = 12
        mock_quiz.get_formatted_created_at.return_value = "2024-01-01T12:00:00Z"

        mock_participation = Mock(spec=Participation)
        mock_participation.quiz = mock_quiz
        mock_participation.score = None
        mock_participation.status = "in_progress"
        mock_participation.get_formatted_completed_at.return_value = None
        mock_participation.get_formatted_created_at.return_value = "2024-01-01T12:30:00Z"

        self.participation_repository_mock.find_all_by_user_id.return_value = [mock_participation]

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetUserQuizzesResponse)
        self.assertEqual(result.total_count, 1)
        participation = result.quizzes_participations[0]
        self.assertIsNone(participation.score)
        self.assertEqual(participation.participation_status, "in_progress")
        self.assertIsNone(participation.completed_at)

    def test_handle_success_with_zero_score(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id_1
        mock_quiz.title = "Failed Quiz"
        mock_quiz.description = "Got zero score"
        mock_quiz.total_questions = 3
        mock_quiz.total_participants = 50
        mock_quiz.get_formatted_created_at.return_value = "2024-01-01T12:00:00Z"

        mock_participation = Mock(spec=Participation)
        mock_participation.quiz = mock_quiz
        mock_participation.score = 0
        mock_participation.status = "completed"
        mock_participation.get_formatted_completed_at.return_value = "2024-01-01T13:00:00Z"
        mock_participation.get_formatted_created_at.return_value = "2024-01-01T12:30:00Z"

        self.participation_repository_mock.find_all_by_user_id.return_value = [mock_participation]

        result = self.handler.handle(self.query)

        self.assertIsInstance(result, GetUserQuizzesResponse)
        self.assertEqual(result.total_count, 1)
        participation = result.quizzes_participations[0]
        self.assertEqual(participation.score, 0)
        self.assertEqual(participation.participation_status, "completed")

    def test_response_as_dict_structure(self):
        mock_quiz = Mock(spec=Quiz)
        mock_quiz.id = self.quiz_id_1
        mock_quiz.title = "Dict Test Quiz"
        mock_quiz.description = "Testing dict conversion"
        mock_quiz.total_questions = 7
        mock_quiz.total_participants = 20
        mock_quiz.get_formatted_created_at.return_value = "2024-01-01T12:00:00Z"

        mock_participation = Mock(spec=Participation)
        mock_participation.quiz = mock_quiz
        mock_participation.score = 95
        mock_participation.status = "completed"
        mock_participation.get_formatted_completed_at.return_value = "2024-01-01T13:00:00Z"
        mock_participation.get_formatted_created_at.return_value = "2024-01-01T12:30:00Z"

        self.participation_repository_mock.find_all_by_user_id.return_value = [mock_participation]

        result = self.handler.handle(self.query)
        result_dict = result.as_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["total_count"], 1)
        self.assertIn("participations", result_dict)
        self.assertEqual(len(result_dict["participations"]), 1)

        participation_dict = result_dict["participations"][0]
        self.assertEqual(participation_dict["quiz_id"], str(self.quiz_id_1))
        self.assertEqual(participation_dict["quiz_title"], "Dict Test Quiz")
        self.assertEqual(participation_dict["score"], 95)
        self.assertEqual(participation_dict["status"], "completed")

    def test_participation_repository_called_with_correct_parameters(self):
        different_user_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        query_with_different_user = GetUserQuizzesQuery(requester_id=different_user_id)

        self.participation_repository_mock.find_all_by_user_id.return_value = []

        self.handler.handle(query_with_different_user)

        self.participation_repository_mock.find_all_by_user_id.assert_called_once_with(
            user_id=different_user_id, related_attributes=[ParticipationRelatedAttribute.QUIZ]
        )
