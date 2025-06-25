from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParticipationData:
    status: str
    invited_at: str
    completed_at: str | None
    score: int | None
    score_percentage: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "invited_at": self.invited_at,
            "completed_at": self.completed_at,
            "score": self.score,
            "score_percentage": self.score_percentage,
        }


@dataclass(frozen=True)
class GetUserQuizProgressResponse:
    quiz_id: str
    quiz_title: str
    quiz_description: str
    total_questions: int
    total_possible_points: int
    quiz_created_at: str
    participation: ParticipationData

    def as_dict(self) -> dict[str, Any]:
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.quiz_title,
            "quiz_description": self.quiz_description,
            "total_questions": self.total_questions,
            "total_possible_points": self.total_possible_points,
            "quiz_created_at": self.quiz_created_at,
            "participation": self.participation.as_dict(),
        }
