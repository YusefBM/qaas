from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class QuizAnswer:
    answer_id: UUID
    text: str
    order: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "answer_id": str(self.answer_id),
            "text": self.text,
            "order": self.order,
        }


@dataclass(frozen=True)
class QuizQuestion:
    question_id: UUID
    text: str
    order: int
    answers: list[QuizAnswer]

    def as_dict(self) -> dict[str, Any]:
        return {
            "question_id": str(self.question_id),
            "text": self.text,
            "order": self.order,
            "answers": [answer.as_dict() for answer in self.answers],
        }


@dataclass(frozen=True)
class GetQuizQueryResponse:
    quiz_id: UUID
    title: str
    description: str
    questions: list[QuizQuestion]

    def as_dict(self) -> dict[str, Any]:
        return {
            "quiz_id": str(self.quiz_id),
            "title": self.title,
            "description": self.description,
            "questions": [question.as_dict() for question in self.questions],
        }
