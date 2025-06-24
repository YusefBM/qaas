from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SendInvitationEmailCommand:
    invitation_id: UUID
    invitation_acceptance_link: str
