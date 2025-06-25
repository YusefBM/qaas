from uuid import UUID

from django.db import IntegrityError

from quiz.domain.quiz.quiz import Quiz
from quiz.domain.quiz.quiz_already_exists_exception import QuizAlreadyExistsException
from quiz.domain.quiz.quiz_not_found_exception import QuizNotFoundException
from quiz.domain.quiz.quiz_repository import QuizRepository


class DbQuizRepository(QuizRepository):
    __UNIQUE_CONSTRAINT_TITLE_AND_CREATOR = "quiz_quiz_title_creator_id"

    def save(self, quiz: Quiz) -> None:
        try:
            quiz.save()
        except IntegrityError as exc:
            if self.__is_unique_constraint_violation(exc):
                raise QuizAlreadyExistsException(title=quiz.title, creator_id=quiz.creator_id) from exc
            raise exc

    def find_or_fail_by_id(self, quiz_id: UUID) -> Quiz:
        try:
            return Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist as e:
            raise QuizNotFoundException(quiz_id=str(quiz_id)) from e

    def find_by_creator_id(self, creator_id: UUID) -> list[Quiz]:
        return list(Quiz.objects.filter(creator_id=creator_id).order_by("-created_at"))

    def __is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_TITLE_AND_CREATOR in exc.__cause__.diag.constraint_name
