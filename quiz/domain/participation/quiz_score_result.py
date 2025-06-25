from dataclasses import dataclass

from quiz.domain.participation.answer_submission import AnswerSubmission


@dataclass(frozen=True)
class QuizScoreResult:
    total_score: int
    total_possible_score: int
    answer_submissions: list[AnswerSubmission]


@dataclass(frozen=True)
class SubmittedAnswer:
    question_id: int
    answer_id: int
