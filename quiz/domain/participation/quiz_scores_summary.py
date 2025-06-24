from dataclasses import dataclass


@dataclass(frozen=True)
class QuizScoresSummary:
    total_participants: int
    average_score: float
    max_score: float
    min_score: float
    top_scorer_email: str
