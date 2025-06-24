from dataclasses import dataclass
from typing import List

from quiz.domain.participation.answer_submission import AnswerSubmission


@dataclass(frozen=True)
class QuizScoreResult:
    total_score: int
    total_possible_score: int
    answer_submissions: List[AnswerSubmission]


@dataclass(frozen=True)
class SubmittedAnswer:
    question_id: int
    answer_id: int

    def __post_init__(self) -> None:
        if self.question_id <= 0:
            raise ValueError("Question ID must be positive")
        if self.answer_id <= 0:
            raise ValueError("Answer ID must be positive")
