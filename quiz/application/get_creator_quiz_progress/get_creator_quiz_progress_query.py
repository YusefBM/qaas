from dataclasses import dataclass


@dataclass(frozen=True)
class GetCreatorQuizProgressQuery:
    quiz_id: str
    requester_id: str
