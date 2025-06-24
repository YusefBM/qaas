from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AcceptInvitationCommand:
    invitation_id: UUID
    user_id: UUID
