import unittest
from unittest.mock import Mock
from uuid import UUID

from rest_framework import status
from voluptuous import MultipleInvalid

from quiz.application.submit_quiz_answers.submit_quiz_answers_response import SubmitQuizAnswersResponse
from quiz.domain.participation.duplicate_answer_submission_exception import DuplicateAnswerSubmissionException
from quiz.domain.participation.incomplete_quiz_submission_exception import IncompleteQuizSubmissionException
from quiz.domain.participation.participation_not_found_for_quiz_and_participant_exception import (
    ParticipationNotFoundForQuizAndParticipantException,
)
from quiz.domain.participation.quiz_already_completed_exception import QuizAlreadyCompletedException
from quiz.domain.quiz.invalid_answer_for_question_exception import InvalidAnswerForQuestionException
from quiz.domain.quiz.invalid_question_for_quiz_exception import InvalidQuestionForQuizException
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.views.submit_quiz_answers_view import SubmitQuizAnswersView
from user.domain.user import User
from user.domain.user_not_found_exception import UserNotFoundException


class TestSubmitQuizAnswersView(unittest.TestCase):
    def setUp(self):
        self.quiz_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.user_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participation_id = UUID("11111111-2222-3333-4444-555555555555")
        self.question_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        self.answer_id = UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff")

        self.mock_user = Mock(spec=User)
        self.mock_user.id = self.user_id

        self.valid_answers_data = {"answers": [{"question_id": self.question_id, "answer_id": self.answer_id}]}

        self.mock_request = Mock()
        self.mock_request.user = self.mock_user
        self.mock_request.data = self.valid_answers_data

        self.mock_command_handler = Mock()
        self.mock_schema = Mock()
        self.mock_logger = Mock()
        self.view = SubmitQuizAnswersView(
            command_handler=self.mock_command_handler, schema=self.mock_schema, logger=self.mock_logger
        )

    def test_post_success(self):
        mock_response = SubmitQuizAnswersResponse(
            message="Quiz completed successfully",
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="JavaScript Fundamentals",
            score=85,
            total_possible_score=100,
            completed_at="2024-01-15T10:30:00.000000Z",
        )

        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Quiz completed successfully")
        self.assertEqual(response.data["participation_id"], str(self.participation_id))
        self.assertEqual(response.data["quiz_id"], str(self.quiz_id))
        self.assertEqual(response.data["quiz_title"], "JavaScript Fundamentals")
        self.assertEqual(response.data["score"], 85)
        self.assertEqual(response.data["total_possible_score"], 100)
        self.assertEqual(response.data["completed_at"], "2024-01-15T10:30:00.000000Z")

        self.mock_command_handler.handle.assert_called_once()
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.participant_id, self.user_id)
        self.assertEqual(command_arg.quiz_id, self.quiz_id)
        self.assertEqual(len(command_arg.answers), 1)
        self.assertEqual(command_arg.answers[0].question_id, self.question_id)
        self.assertEqual(command_arg.answers[0].answer_id, self.answer_id)

    def test_post_handles_non_dict_request_data(self):
        self.mock_request.data = "not a dict"

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Body request must be a JSON object")

    def test_post_handles_validation_error(self):
        self.mock_schema.side_effect = MultipleInvalid("Invalid answer format")

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_malformed_request_body_exception(self):
        self.mock_schema.side_effect = Exception("Malformed JSON")

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Malformed request body")

    def test_post_handles_participation_not_found_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = ParticipationNotFoundForQuizAndParticipantException(
            quiz_id=str(self.quiz_id), participant_id=str(self.user_id)
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_handles_quiz_already_completed_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = QuizAlreadyCompletedException(
            quiz_id=str(self.quiz_id), user_id=str(self.user_id)
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_post_handles_incomplete_quiz_submission_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = IncompleteQuizSubmissionException(
            quiz_id=self.quiz_id, expected_answers=3, received_answers=2
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_duplicate_answer_submission_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = DuplicateAnswerSubmissionException(
            question_id=str(self.question_id)
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_invalid_question_for_quiz_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = InvalidQuestionForQuizException(
            quiz_id=str(self.quiz_id), question_id=str(self.question_id)
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_invalid_answer_for_question_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = InvalidAnswerForQuestionException(
            question_id=str(self.question_id), answer_id=str(self.answer_id)
        )

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_handles_quiz_not_found_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = QuizNotFoundException(str(self.quiz_id))

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_handles_user_not_found_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = UserNotFoundException(str(self.user_id))

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_handles_unexpected_exception(self):
        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.side_effect = Exception("Unexpected error")

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Internal server error when submitting quiz answers")

    def test_post_with_different_quiz_id(self):
        different_quiz_id = UUID("99999999-8888-7777-6666-555555555555")
        mock_response = SubmitQuizAnswersResponse(
            message="Different quiz completed",
            participation_id=self.participation_id,
            quiz_id=different_quiz_id,
            quiz_title="Python Advanced",
            score=90,
            total_possible_score=100,
            completed_at="2024-01-20T14:15:00.000000Z",
        )

        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, different_quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quiz_id"], str(different_quiz_id))
        self.assertEqual(response.data["quiz_title"], "Python Advanced")

    def test_post_with_different_user(self):
        different_user_id = UUID("77777777-6666-5555-4444-333333333333")
        different_user = Mock(spec=User)
        different_user.id = different_user_id

        different_request = Mock()
        different_request.user = different_user
        different_request.data = self.valid_answers_data

        mock_response = SubmitQuizAnswersResponse(
            message="Quiz completed by different user",
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Django Basics",
            score=75,
            total_possible_score=100,
            completed_at="2024-01-25T09:00:00.000000Z",
        )

        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(different_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(command_arg.participant_id, different_user_id)

    def test_post_with_multiple_answers(self):
        multiple_answers_data = {
            "answers": [
                {"question_id": self.question_id, "answer_id": self.answer_id},
                {
                    "question_id": UUID("cccccccc-dddd-eeee-ffff-000000000000"),
                    "answer_id": UUID("dddddddd-eeee-ffff-0000-111111111111"),
                },
            ]
        }

        self.mock_request.data = multiple_answers_data
        mock_response = SubmitQuizAnswersResponse(
            message="Quiz with multiple answers completed",
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Multi-Question Quiz",
            score=95,
            total_possible_score=100,
            completed_at="2024-02-01T16:45:00.000000Z",
        )

        self.mock_schema.return_value = multiple_answers_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        command_arg = self.mock_command_handler.handle.call_args[0][0]
        self.assertEqual(len(command_arg.answers), 2)
        self.assertEqual(command_arg.answers[0].question_id, self.question_id)
        self.assertEqual(command_arg.answers[1].question_id, UUID("cccccccc-dddd-eeee-ffff-000000000000"))

    def test_post_with_perfect_score(self):
        mock_response = SubmitQuizAnswersResponse(
            message="Perfect score achieved",
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Perfect Quiz",
            score=100,
            total_possible_score=100,
            completed_at="2024-02-05T12:00:00.000000Z",
        )

        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 100)
        self.assertEqual(response.data["total_possible_score"], 100)

    def test_post_with_zero_score(self):
        mock_response = SubmitQuizAnswersResponse(
            message="Quiz completed with zero score",
            participation_id=self.participation_id,
            quiz_id=self.quiz_id,
            quiz_title="Challenging Quiz",
            score=0,
            total_possible_score=100,
            completed_at="2024-02-10T08:30:00.000000Z",
        )

        self.mock_schema.return_value = self.valid_answers_data
        self.mock_command_handler.handle.return_value = mock_response

        response = self.view.post(self.mock_request, self.quiz_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 0)
        self.assertEqual(response.data["total_possible_score"], 100)
