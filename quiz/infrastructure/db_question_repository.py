from typing import Dict

from django.db import IntegrityError

from quiz.domain.quiz.question import Question
from quiz.domain.quiz.question_already_exists_exception import QuestionAlreadyExistsException
from quiz.domain.quiz.question_repository import QuestionRepository


class DbQuestionRepository(QuestionRepository):
    __UNIQUE_CONSTRAINT_TITLE_AND_CREATOR = "quiz_question_quiz_id_order"

    def save(self, question: Question) -> None:
        try:
            question.save()
        except IntegrityError as exc:
            if self.__is_unique_constraint_violation(exc):
                raise QuestionAlreadyExistsException(order=question.order, quiz_id=question.quiz_id) from exc
            raise exc

    def find_by_ids(self, question_ids: list[int]) -> Dict[int, Question]:
        questions = Question.objects.filter(id__in=question_ids)
        return {question.id: question for question in questions}

    def __is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_TITLE_AND_CREATOR in exc.__cause__.diag.constraint_name
