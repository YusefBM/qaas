from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class Participation:
    status: str
    invited_at: str
    completed_at: Optional[str]
    my_score: Optional[int]
    score_percentage: Optional[float]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "invited_at": self.invited_at,
            "completed_at": self.completed_at,
            "my_score": self.my_score,
            "score_percentage": round(self.score_percentage, 2) if self.score_percentage else None,
        }


@dataclass(frozen=True)
class GetUserQuizProgressResponse:
    quiz_id: str
    quiz_title: str
    quiz_description: str
    total_questions: int
    total_possible_points: int
    quiz_created_at: str

    my_participation: Participation

    def as_dict(self) -> Dict[str, Any]:
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.quiz_title,
            "quiz_description": self.quiz_description,
            "total_questions": self.total_questions,
            "total_possible_points": self.total_possible_points,
            "quiz_created_at": self.quiz_created_at,
            "my_participation": self.my_participation.as_dict(),
        }
