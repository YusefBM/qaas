from dataclasses import dataclass


@dataclass(frozen=True)
class GetQuizScoresQuery:
    quiz_id: str
    requester_id: str
