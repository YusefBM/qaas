from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InvitationStats:
    total_sent: int
    total_accepted: int
    acceptance_rate: float
    pending_invitations: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_sent": self.total_sent,
            "total_accepted": self.total_accepted,
            "acceptance_rate": self.acceptance_rate,
            "pending_invitations": self.pending_invitations,
        }


@dataclass(frozen=True)
class ParticipationStats:
    total_participants: int
    completed_participants: int
    completion_rate: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_participants": self.total_participants,
            "completed_participants": self.completed_participants,
            "completion_rate": self.completion_rate,
        }


@dataclass(frozen=True)
class GetCreatorQuizProgressResponse:
    quiz_id: str
    quiz_title: str
    quiz_description: str
    total_questions: int
    created_at: str
    invitation_stats: InvitationStats
    participation_stats: ParticipationStats

    def as_dict(self) -> dict[str, Any]:
        return {
            "quiz_id": self.quiz_id,
            "quiz_title": self.quiz_title,
            "quiz_description": self.quiz_description,
            "total_questions": self.total_questions,
            "created_at": self.created_at,
            "invitation_stats": self.invitation_stats.as_dict(),
            "participation_stats": self.participation_stats.as_dict(),
        }
