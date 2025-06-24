from logging import getLogger

from django.db import transaction
from uuid_utils.compat import uuid7

from quiz.application.create_quiz.create_quiz_command import CreateQuizCommand
from quiz.application.create_quiz.create_quiz_response import CreateQuizResponse
from quiz.application.create_quiz.question_mapper import QuestionMapper
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.answer_repository import AnswerRepository
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.question_repository import QuestionRepository
from quiz.domain.quiz.question_validator import QuestionValidator
from quiz.domain.quiz.question_validator_context import QuestionValidatorContext
from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_repository import QuizRepository
from user.domain.user_repository import UserRepository


class CreateQuizCommandHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        question_mapper: QuestionMapper,
        question_validator: QuestionValidator,
    ) -> None:
        self.__user_repository = user_repository
        self.__quiz_repository = quiz_repository
        self.__question_repository = question_repository
        self.__answer_repository = answer_repository
        self.__question_mapper = question_mapper
        self.__question_validator = question_validator
        self.__logger = getLogger(__name__)

    def handle(self, command: CreateQuizCommand) -> CreateQuizResponse:
        self.__logger.info(f"Creating quiz with title '{command.title}' by user '{command.creator_id}'")

        creator = self.__user_repository.find_or_fail_by_id(user_id=command.creator_id)
        quiz = Quiz(
            id=uuid7(),
            title=command.title,
            description=command.description,
            creator=creator,
        )

        questions_with_answers: list[tuple[Question, list[Answer]]] = []
        for question_data in command.questions:
            question, answers = self.__question_mapper.map_to_domain(quiz, question_data)
            self.__question_validator.validate(context=QuestionValidatorContext(question, answers))
            questions_with_answers.append((question, answers))

        with transaction.atomic():
            self.__quiz_repository.save(quiz)
            for question, answers in questions_with_answers:
                self.__question_repository.save(question)
                self.__answer_repository.bulk_save(answers)

        self.__logger.info(f"Quiz with id {quiz.id} created by user '{command.creator_id}'")

        return CreateQuizResponse(quiz_id=str(quiz.id))
