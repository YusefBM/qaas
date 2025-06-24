from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserQuizProgressQuery:
    quiz_id: str
    requester_id: str
