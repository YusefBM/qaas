from typing import Optional
from uuid import UUID

from django.db.models import Count, Avg, Q, Max, Min, FloatField
from django.db.models.functions import Coalesce

from quiz.application.get_creator_quiz_progress.get_creator_quiz_progress_response import (
    InvitationStats,
    ParticipationStats,
)
from quiz.domain.invitation.invitation import Invitation
from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.participation.quiz_progress_summary import QuizProgressSummary
from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary
from quiz.domain.participation.user_participation_data import UserParticipationData


class DbParticipationFinder(ParticipationFinder):

    def find_quiz_scores_summary(self, quiz_id: UUID) -> QuizScoresSummary:
        stats = Participation.objects.filter(quiz_id=quiz_id).aggregate(
            total_participants=Count("id"),
            average_score=Coalesce(
                Avg("score", filter=Q(completed_at__isnull=False, score__isnull=False)), 0.0, output_field=FloatField()
            ),
            max_score=Coalesce(
                Max("score", filter=Q(completed_at__isnull=False, score__isnull=False)), 0.0, output_field=FloatField()
            ),
            min_score=Coalesce(
                Min("score", filter=Q(completed_at__isnull=False, score__isnull=False)), 0.0, output_field=FloatField()
            ),
        )

        top_scorer_participation = (
            Participation.objects.filter(quiz_id=quiz_id, completed_at__isnull=False, score__isnull=False)
            .select_related("participant")
            .order_by("-score")
            .first()
        )

        return QuizScoresSummary(
            total_participants=stats["total_participants"],
            average_score=round(float(stats["average_score"]), 2),
            max_score=round(float(stats["max_score"]), 2),
            min_score=round(float(stats["min_score"]), 2),
            top_scorer_email=top_scorer_participation.participant.email if top_scorer_participation else None,
        )

    def find_user_participation_for_quiz(self, quiz_id: UUID, user_id: UUID) -> Optional[UserParticipationData]:
        try:
            participation = Participation.objects.select_related("invitation").get(
                quiz_id=quiz_id, participant_id=user_id
            )

            invited_at = None
            if participation.invitation is not None:
                invited_at = participation.invitation.get_formatted_invited_at()

            started_at = participation.get_formatted_created_at()

            return UserParticipationData(
                status=participation.status.value,
                invited_at=invited_at,
                started_at=started_at,
                completed_at=participation.get_formatted_completed_at(),
                my_score=participation.score,
            )
        except Participation.DoesNotExist:
            return None

    def find_creator_quiz_progress_summary(self, quiz_id: UUID) -> QuizProgressSummary:
        invitation_stats = Invitation.objects.filter(quiz_id=quiz_id).aggregate(
            total_sent=Count("id"),
            total_accepted=Count("id", filter=Q(accepted_at__isnull=False)),
        )

        total_sent = invitation_stats["total_sent"]
        total_accepted = invitation_stats["total_accepted"]
        acceptance_rate = (total_accepted / total_sent * 100) if total_sent > 0 else 0.0
        pending_invitations = total_sent - total_accepted

        participation_stats = Participation.objects.filter(quiz_id=quiz_id).aggregate(
            total_participants=Count("id"),
            completed_participants=Count("id", filter=Q(completed_at__isnull=False)),
        )

        total_participants = participation_stats["total_participants"]
        completed_participants = participation_stats["completed_participants"]
        completion_rate = (completed_participants / total_participants * 100) if total_participants > 0 else 0.0

        return QuizProgressSummary(
            invitation_stats=InvitationStats(
                total_sent=total_sent,
                total_accepted=total_accepted,
                acceptance_rate=round(acceptance_rate, 2),
                pending_invitations=pending_invitations,
            ),
            participation_stats=ParticipationStats(
                total_participants=total_participants,
                completed_participants=completed_participants,
                completion_rate=round(completion_rate, 2),
            ),
        )
