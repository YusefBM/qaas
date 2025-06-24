from dataclasses import dataclass

from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_response import (
    InvitationStats,
    ParticipationStats,
)


@dataclass(frozen=True)
class QuizProgressSummary:
    invitation_stats: InvitationStats
    participation_stats: ParticipationStats
