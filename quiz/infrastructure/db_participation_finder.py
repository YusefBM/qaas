from uuid import UUID

from django.db.models import Count, Avg, Q, Max, Min, FloatField
from django.db.models.functions import Coalesce

from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_finder import ParticipationFinder
from quiz.domain.participation.quiz_scores_summary import QuizScoresSummary


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
