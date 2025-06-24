from typing import Optional, Dict

from django.db import IntegrityError

from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.answer_already_exists_exception import AnswerAlreadyExistsException
from quiz.domain.quiz.answer_repository import AnswerRepository


class DbAnswerRepository(AnswerRepository):
    __UNIQUE_CONSTRAINT_QUESTION_AND_ORDER = "quiz_answer_question_id_order"

    def save(self, answer: Answer) -> None:
        try:
            answer.save()
        except IntegrityError as exc:
            if self._is_unique_constraint_violation(exc):
                raise AnswerAlreadyExistsException(order=answer.order, question_id=answer.question_id)
            raise exc

    def find_by_id(self, answer_id: int) -> Optional[Answer]:
        try:
            return Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return None

    def find_by_ids(self, answer_ids: list[int]) -> Dict[int, Answer]:
        answers = Answer.objects.filter(id__in=answer_ids)
        return {answer.id: answer for answer in answers}

    def _is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_QUESTION_AND_ORDER in exc.__cause__.diag.constraint_name

    def bulk_save(self, answers: list[Answer]) -> None:
        for answer in answers:
            self.save(answer)
