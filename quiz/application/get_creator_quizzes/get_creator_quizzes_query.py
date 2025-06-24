from dataclasses import dataclass


@dataclass(frozen=True)
class GetCreatorQuizzesQuery:
    creator_id: str
