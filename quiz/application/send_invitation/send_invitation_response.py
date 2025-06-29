from dataclasses import dataclass


@dataclass(frozen=True)
class SendInvitationResponse:
    invitation_id: str
    quiz_title: str
    participant_email: str
    invited_at: str
    invitation_acceptance_link: str

    def as_dict(self) -> dict:
        return {
            "invitation_id": self.invitation_id,
            "quiz_title": self.quiz_title,
            "participant_email": self.participant_email,
            "invited_at": self.invited_at,
            "invitation_acceptance_link": self.invitation_acceptance_link,
        }
