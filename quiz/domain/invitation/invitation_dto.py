from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class InvitationDto:
    """DTO for invitation data - contains only primitive types and other DTOs"""

    invitation_id: UUID
    quiz_id: UUID
    inviter_id: UUID
    invitee_id: UUID
    invitee_email: str
    is_accepted: bool
    created_at: datetime
    accepted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if invitation has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
