from django.db import IntegrityError

from quiz.domain.participation.answer_submission import AnswerSubmission
from quiz.domain.participation.answer_submission_repository import AnswerSubmissionRepository
from quiz.domain.participation.duplicate_answer_submission_exception import DuplicateAnswerSubmissionException


class DbAnswerSubmissionRepository(AnswerSubmissionRepository):
    __UNIQUE_CONSTRAINT_PARTICIPATION_AND_QUESTION = "quiz_answersubmission_participation_id_question_id"

    def save(self, answer_submission: AnswerSubmission) -> None:
        try:
            answer_submission.save()
        except IntegrityError as exc:
            if self._is_unique_constraint_violation(exc):
                raise DuplicateAnswerSubmissionException(question_id=answer_submission.question.id)
            raise exc

    def bulk_save(self, answer_submissions: list[AnswerSubmission]) -> None:
        for answer_submission in answer_submissions:
            self.save(answer_submission)

    def _is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_PARTICIPATION_AND_QUESTION in exc.__cause__.diag.constraint_name
