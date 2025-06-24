from django.db import models
from django.utils import timezone
from uuid_utils.compat import uuid7

from quiz.domain.participation.participation_status import ParticipationStatus
from quiz.domain.quiz.quiz import Quiz
from user.domain.user import User


class Participation(models.Model):
    __UTC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    id = models.UUIDField(primary_key=True, default=uuid7)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, related_name="participations")
    participant = models.ForeignKey(User, on_delete=models.PROTECT, related_name="quiz_participations")
    invitation = models.ForeignKey(
        "quiz.Invitation", on_delete=models.PROTECT, related_name="participation", null=True, blank=True
    )
    score = models.PositiveIntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["quiz", "participant"]

    @property
    def status(self) -> ParticipationStatus:
        if self.completed_at:
            return ParticipationStatus.COMPLETED

        return ParticipationStatus.INVITED

    def get_formatted_completed_at(self) -> str | None:
        if self.completed_at:
            return self.completed_at.strftime(self.__UTC_DATETIME_FORMAT)

        return None

    def get_formatted_created_at(self) -> str:
        return self.created_at.strftime(self.__UTC_DATETIME_FORMAT)

    def complete(self, score: int) -> None:
        self.score = score
        self.completed_at = timezone.now()

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def __str__(self):
        return f"{self.participant.email} - {self.quiz.title} ({self.status})"
