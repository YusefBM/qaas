import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.application.get_quiz_query.get_quiz_query import GetQuizQuery
from quiz.application.get_quiz_query.get_quiz_query_handler import GetQuizQueryHandler
from quiz.application.get_quiz_query.get_quiz_query_response import GetQuizQueryResponse
from quiz.application.get_quiz_query.quiz_data_mapper import QuizDataMapper
from quiz.domain.invitation.invitation_repository import InvitationRepository
from quiz.domain.participation.participation_repository import ParticipationRepository
from quiz.domain.quiz.quiz_data import QuizData, QuestionData, AnswerData
from quiz.domain.quiz.quiz_finder import QuizFinder
from quiz.domain.quiz.unauthorized_quiz_access_exception import UnauthorizedQuizAccessException


class TestGetQuizQueryHandler(unittest.TestCase):
    def setUp(self):
        self.quiz_finder_mock = Mock(spec=QuizFinder)
        self.participation_repository_mock = Mock(spec=ParticipationRepository)
        self.invitation_repository_mock = Mock(spec=InvitationRepository)
        self.mapper_mock = Mock(spec=QuizDataMapper)

        self.handler = GetQuizQueryHandler(
            quiz_finder=self.quiz_finder_mock,
            participation_repository=self.participation_repository_mock,
            invitation_repository=self.invitation_repository_mock,
            mapper=self.mapper_mock,
        )

        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.participant_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.creator_id = UUID("11111111-2222-3333-4444-555555555555")

        self.query = GetQuizQuery(participant_id=self.participant_id, quiz_id=self.quiz_id)

    def test_handle_success_for_creator(self):
        answer_data = AnswerData(answer_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"), text="Correct answer", order=1)

        question_data = QuestionData(
            question_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            text="What is 2 + 2?",
            order=1,
            points=10,
            answers=[answer_data],
        )

        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Math Quiz",
            quiz_description="Basic math questions",
            quiz_creator_id=self.participant_id,  # User is the creator
            questions=[question_data],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(self.query)

        self.assertEqual(result, mock_response)
        self.quiz_finder_mock.find_quiz_for_participation.assert_called_once_with(
            quiz_id=self.quiz_id, participant_id=self.participant_id
        )
        self.mapper_mock.map_to_response.assert_called_once_with(quiz_data)
        self.participation_repository_mock.exists_by_quiz_and_participant.assert_not_called()
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_not_called()

    def test_handle_success_with_participation(self):
        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Science Quiz",
            quiz_description="Physics and chemistry",
            quiz_creator_id=self.creator_id,  # Different from participant
            questions=[],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.participation_repository_mock.exists_by_quiz_and_participant.return_value = True
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(self.query)

        self.assertEqual(result, mock_response)
        self.participation_repository_mock.exists_by_quiz_and_participant.assert_called_once_with(
            self.quiz_id, self.participant_id
        )
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_not_called()

    def test_handle_success_with_invitation(self):
        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="History Quiz",
            quiz_description="World history",
            quiz_creator_id=self.creator_id,
            questions=[],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.participation_repository_mock.exists_by_quiz_and_participant.return_value = False
        self.invitation_repository_mock.exists_by_quiz_and_invited.return_value = True
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(self.query)

        self.assertEqual(result, mock_response)
        self.participation_repository_mock.exists_by_quiz_and_participant.assert_called_once_with(
            self.quiz_id, self.participant_id
        )
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_called_once_with(
            quiz_id=self.quiz_id, invited_id=self.participant_id
        )

    def test_handle_unauthorized_access_raises_exception(self):
        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Private Quiz",
            quiz_description="Restricted access",
            quiz_creator_id=self.creator_id,  # Different from participant
            questions=[],
        )

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.participation_repository_mock.exists_by_quiz_and_participant.return_value = False
        self.invitation_repository_mock.exists_by_quiz_and_invited.return_value = False

        with self.assertRaises(UnauthorizedQuizAccessException) as context:
            self.handler.handle(self.query)

        self.assertEqual(context.exception.quiz_id, "12345678-1234-5678-9abc-123456789abc")
        self.assertEqual(context.exception.user_id, "87654321-4321-8765-cba9-987654321098")

        self.participation_repository_mock.exists_by_quiz_and_participant.assert_called_once_with(
            self.quiz_id, self.participant_id
        )
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_called_once_with(
            quiz_id=self.quiz_id, invited_id=self.participant_id
        )
        self.mapper_mock.map_to_response.assert_not_called()

    def test_handle_authorization_check_priority(self):
        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Mixed Access Quiz",
            quiz_description="Multiple access levels",
            quiz_creator_id=self.participant_id,  # User is creator
            questions=[],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(self.query)

        self.assertEqual(result, mock_response)
        self.participation_repository_mock.exists_by_quiz_and_participant.assert_not_called()
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_not_called()

    def test_handle_complex_quiz_with_multiple_questions(self):
        answer1 = AnswerData(answer_id=UUID("11111111-1111-1111-1111-111111111111"), text="Option A", order=1)
        answer2 = AnswerData(answer_id=UUID("22222222-2222-2222-2222-222222222222"), text="Option B", order=2)

        question1 = QuestionData(
            question_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            text="Question 1",
            order=1,
            points=5,
            answers=[answer1, answer2],
        )

        question2 = QuestionData(
            question_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            text="Question 2",
            order=2,
            points=10,
            answers=[answer1, answer2],
        )

        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Complex Quiz",
            quiz_description="Multiple questions and answers",
            quiz_creator_id=self.participant_id,
            questions=[question1, question2],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(self.query)

        self.assertEqual(result, mock_response)
        self.mapper_mock.map_to_response.assert_called_once_with(quiz_data)

    def test_handle_participation_exists_but_no_invitation(self):
        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Participation Only Quiz",
            quiz_description="Has participation but no invitation",
            quiz_creator_id=self.creator_id,
            questions=[],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.participation_repository_mock.exists_by_quiz_and_participant.return_value = True
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(self.query)

        self.assertEqual(result, mock_response)
        self.participation_repository_mock.exists_by_quiz_and_participant.assert_called_once_with(
            self.quiz_id, self.participant_id
        )
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_not_called()

    def test_handle_neither_participation_nor_invitation_exists(self):
        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Restricted Quiz",
            quiz_description="No access granted",
            quiz_creator_id=self.creator_id,
            questions=[],
        )

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.participation_repository_mock.exists_by_quiz_and_participant.return_value = False
        self.invitation_repository_mock.exists_by_quiz_and_invited.return_value = False

        with self.assertRaises(UnauthorizedQuizAccessException):
            self.handler.handle(self.query)

        self.participation_repository_mock.exists_by_quiz_and_participant.assert_called_once_with(
            self.quiz_id, self.participant_id
        )
        self.invitation_repository_mock.exists_by_quiz_and_invited.assert_called_once_with(
            quiz_id=self.quiz_id, invited_id=self.participant_id
        )

    def test_handle_different_participant_id(self):
        different_participant_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        different_query = GetQuizQuery(participant_id=different_participant_id, quiz_id=self.quiz_id)

        quiz_data = QuizData(
            quiz_id=self.quiz_id,
            quiz_title="Another Quiz",
            quiz_description="Different participant",
            quiz_creator_id=different_participant_id,  # User is creator
            questions=[],
        )

        mock_response = Mock(spec=GetQuizQueryResponse)

        self.quiz_finder_mock.find_quiz_for_participation.return_value = quiz_data
        self.mapper_mock.map_to_response.return_value = mock_response

        result = self.handler.handle(different_query)

        self.assertEqual(result, mock_response)
        self.quiz_finder_mock.find_quiz_for_participation.assert_called_once_with(
            quiz_id=self.quiz_id, participant_id=different_participant_id
        )
