from dataclasses import dataclass


@dataclass(frozen=True)
class SendInvitationCommand:
    quiz_id: str
    participant_email: str
    inviter_id: str
    inviter_email: str
