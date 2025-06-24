from dataclasses import dataclass

from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.question import Question


@dataclass(frozen=True)
class QuestionValidatorContext:
    question: Question
    answers: list[Answer]
