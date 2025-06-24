from dataclasses import dataclass


@dataclass(frozen=True)
class GetQuizScoresResponse:
    quiz_id: str
    quiz_title: str
    total_participants: int
    average_score: float
    max_score: float
    min_score: float
    top_scorer_email: str

    def as_dict(self) -> dict:
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.quiz_title,
            "total_participants": self.total_participants,
            "average_score": self.average_score,
            "max_score": self.max_score,
            "min_score": self.min_score,
            "top_scorer_email": self.top_scorer_email,
        }
