from dataclasses import dataclass
from typing import Dict, Any
from uuid import UUID


@dataclass(frozen=True)
class AcceptInvitationResponse:
    message: str
    invitation_id: UUID
    participation_id: UUID
    quiz_id: UUID
    quiz_title: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "invitation_id": str(self.invitation_id),
            "participation_id": str(self.participation_id),
            "quiz_id": str(self.quiz_id),
            "quiz_title": self.quiz_title,
        }
