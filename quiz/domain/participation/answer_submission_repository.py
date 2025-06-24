from abc import ABC, abstractmethod

from quiz.domain.participation.answer_submission import AnswerSubmission


class AnswerSubmissionRepository(ABC):
    @abstractmethod
    def save(self, answer_submission: AnswerSubmission) -> None:
        pass

    @abstractmethod
    def bulk_save(self, answer_submissions: list[AnswerSubmission]) -> None:
        pass
