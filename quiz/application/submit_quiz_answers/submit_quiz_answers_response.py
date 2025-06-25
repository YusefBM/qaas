from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class SubmitQuizAnswersResponse:
    message: str
    participation_id: UUID
    quiz_id: UUID
    quiz_title: str
    score: int
    total_possible_score: int
    completed_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "participation_id": str(self.participation_id),
            "quiz_id": str(self.quiz_id),
            "quiz_title": self.quiz_title,
            "score": self.score,
            "total_possible_score": self.total_possible_score,
            "completed_at": self.completed_at,
        }
