from logging import getLogger
from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView
from voluptuous import MultipleInvalid

from quiz.application.submit_quiz_answers.submit_quiz_answers_command import SubmitQuizAnswersCommand, SubmittedAnswer
from quiz.application.submit_quiz_answers.submit_quiz_answers_command_handler_factory import (
    SubmitQuizAnswersCommandHandlerFactory,
)
from quiz.domain.participation.duplicate_answer_submission_exception import DuplicateAnswerSubmissionException
from quiz.domain.participation.incomplete_quiz_submission_exception import IncompleteQuizSubmissionException
from quiz.domain.participation.participation_not_found_for_quiz_and_participant_exception import (
    ParticipationNotFoundForQuizAndParticipantException,
)
from quiz.domain.participation.quiz_already_completed_exception import QuizAlreadyCompletedException
from quiz.domain.quiz.invalid_answer_for_question_exception import InvalidAnswerForQuestionException
from quiz.domain.quiz.invalid_question_for_quiz_exception import InvalidQuestionForQuizException
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.infrastructure.views.submit_quiz_answers_view_schema import submit_quiz_answers_view_schema
from user.domain.user_not_found_exception import UserNotFoundException


class SubmitQuizAnswersView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__schema = submit_quiz_answers_view_schema
        self.__command_handler = SubmitQuizAnswersCommandHandlerFactory.create()
        self.__logger = getLogger(__name__)

    def post(self, request: Request, quiz_id: UUID) -> Response:
        try:
            if isinstance(request.data, dict) is False:
                return Response(
                    {
                        "message": "Body request must be a JSON object",
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            validated_body = self.__get_validated_request_body(body=request.data)
        except MultipleInvalid as error:
            return Response(
                {
                    "message": f"{error}",
                },
                status=HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            self.__logger.exception(f"Error submitting quiz answers: '{error}'")
            return Response({"message": "Malformed request body"}, status=HTTP_400_BAD_REQUEST)

        try:
            submitted_answers = [
                SubmittedAnswer(
                    question_id=answer_data["question_id"],
                    answer_id=answer_data["answer_id"],
                )
                for answer_data in validated_body["answers"]
            ]

            command = SubmitQuizAnswersCommand(
                participant_id=request.user.id,
                quiz_id=quiz_id,
                answers=submitted_answers,
            )

            response = self.__command_handler.handle(command)

            self.__logger.info(
                "Quiz submission completed successfully",
                extra={
                    "quiz_id": str(quiz_id),
                    "user_id": str(request.user.id),
                    "score": response.score,
                    "total_possible_score": response.total_possible_score,
                },
            )

            return Response(response.as_dict(), status=status.HTTP_200_OK)

        except ParticipationNotFoundForQuizAndParticipantException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_403_FORBIDDEN,
            )
        except QuizAlreadyCompletedException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_409_CONFLICT,
            )
        except IncompleteQuizSubmissionException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except DuplicateAnswerSubmissionException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except InvalidQuestionForQuizException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except InvalidAnswerForQuestionException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except QuizNotFoundException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_404_NOT_FOUND,
            )
        except UserNotFoundException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_401_UNAUTHORIZED,
            )
        except Exception as error:
            self.__logger.exception(f"Error submitting quiz answers: '{error}'")
            return Response(
                {"message": "Internal server error when submitting quiz answers"}, status=HTTP_500_INTERNAL_SERVER_ERROR
            )

    def __get_validated_request_body(self, body: dict) -> dict:
        return self.__schema(body)
