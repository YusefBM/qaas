from enum import StrEnum


class ParticipationStatus(StrEnum):
    INVITED = "invited"
    COMPLETED = "completed"

    @classmethod
    def get_participable_statuses(cls) -> list[str]:
        return [cls.INVITATION_PENDING, cls.INVITED]
