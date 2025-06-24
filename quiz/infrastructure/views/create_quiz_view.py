from logging import getLogger

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from rest_framework.views import APIView
from voluptuous import MultipleInvalid

from quiz.application.create_quiz.create_quiz_command import CreateQuizCommand
from quiz.application.create_quiz.create_quiz_command_handler_factory import CreateQuizCommandHandlerFactory
from quiz.domain.quiz.answer_already_exists_exception import AnswerAlreadyExistsException
from quiz.domain.quiz.invalid_number_of_answers_exception import InvalidNumberOfAnswersException
from quiz.domain.quiz.invalid_number_of_correct_answers_exception import InvalidNumberOfCorrectAnswersException
from quiz.domain.quiz.question_already_exists_exception import QuestionAlreadyExistsException
from quiz.domain.quiz.quiz_already_exists_exception import QuizAlreadyExistsException
from quiz.infrastructure.views.create_quiz_view_schema import create_quiz_view_schema


class CreateQuizView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__schema = create_quiz_view_schema
        self.__command_handler = CreateQuizCommandHandlerFactory.create()
        self.__logger = getLogger(__name__)

    def post(self, request: Request) -> Response:
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
            self.__logger.exception(f"Error creating a quiz: '{error}'")
            return Response({"message": "Malformed request body"}, status=HTTP_400_BAD_REQUEST)

        try:
            command = CreateQuizCommand(
                title=validated_body["title"],
                description=validated_body["description"],
                creator_id=str(request.user.id),
                questions=validated_body["questions"],
            )
            create_quiz_response = self.__command_handler.handle(command)

            return Response(create_quiz_response.as_dict(), status=status.HTTP_201_CREATED)

        except QuizAlreadyExistsException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_409_CONFLICT,
            )
        except QuestionAlreadyExistsException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_409_CONFLICT,
            )
        except AnswerAlreadyExistsException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_409_CONFLICT,
            )
        except InvalidNumberOfAnswersException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except InvalidNumberOfCorrectAnswersException as error:
            return Response(
                {"message": f"{error}"},
                status=HTTP_400_BAD_REQUEST,
            )
        except Exception as error:
            self.__logger.exception(f"Error creating a quiz: '{error}'")
            return Response(
                {"message": "Internal server error when creating a quiz"}, status=HTTP_500_INTERNAL_SERVER_ERROR
            )

    def __get_validated_request_body(self, body: dict) -> dict:
        return self.__schema(body)
