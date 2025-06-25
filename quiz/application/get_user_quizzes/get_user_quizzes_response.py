from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class QuizParticipationSummary:
    quiz_id: UUID
    quiz_title: str
    quiz_description: str
    total_questions: int
    total_participants: int
    quiz_created_at: str
    participation_status: str
    score: int | None = None
    completed_at: str | None = None
    participation_created_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "quiz_id": str(self.quiz_id),
            "quiz_title": self.quiz_title,
            "quiz_description": self.quiz_description,
            "total_questions": self.total_questions,
            "total_participants": self.total_participants,
            "quiz_created_at": self.quiz_created_at,
            "score": self.score,
            "completed_at": self.completed_at,
            "status": self.participation_status,
            "participation_created_at": self.participation_created_at,
        }


@dataclass(frozen=True)
class GetUserQuizzesResponse:
    quizzes_participations: list[QuizParticipationSummary]
    total_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "user_quizzes": [participation.as_dict() for participation in self.quizzes_participations],
            "total_count": self.total_count,
        }
