from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class QuizSummary:
    id: UUID
    title: str
    description: str
    questions_count: int
    participants_count: int
    created_at: str
    updated_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "questions_count": self.questions_count,
            "participants_count": self.participants_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True)
class GetCreatorQuizzesResponse:
    creator_id: str
    quizzes: list[QuizSummary]
    total_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "creator_id": self.creator_id,
            "total_count": self.total_count,
            "quizzes": [quiz.as_dict() for quiz in self.quizzes],
        }
