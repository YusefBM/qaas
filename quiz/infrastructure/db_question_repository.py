from django.db import IntegrityError
from typing import Optional, Dict

from quiz.domain.quiz.question import Question
from quiz.domain.quiz.question_already_exists_exception import QuestionAlreadyExistsException
from quiz.domain.quiz.question_repository import QuestionRepository


class DbQuestionRepository(QuestionRepository):
    __UNIQUE_CONSTRAINT_TITLE_AND_CREATOR = "quiz_question_quiz_id_order"

    def save(self, question: Question) -> None:
        try:
            question.save()
        except IntegrityError as exc:
            if self._is_unique_constraint_violation(exc):
                raise QuestionAlreadyExistsException(order=question.order, quiz_id=question.quiz_id)
            raise exc

    def find_by_id(self, question_id: int) -> Optional[Question]:
        try:
            return Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return None

    def find_by_ids(self, question_ids: list[int]) -> Dict[int, Question]:
        questions = Question.objects.filter(id__in=question_ids)
        return {question.id: question for question in questions}

    def _is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_TITLE_AND_CREATOR in exc.__cause__.diag.constraint_name
