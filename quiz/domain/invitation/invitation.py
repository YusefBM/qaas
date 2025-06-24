from uuid import UUID

from django.db import models
from django.utils import timezone
from uuid_utils.compat import uuid7

from quiz.domain.quiz.quiz import Quiz
from user.domain.user import User


class Invitation(models.Model):
    __UTC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    id = models.UUIDField(primary_key=True, default=uuid7)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, related_name="invitations")
    invited = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_invitations")
    inviter = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sent_invitations")
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("quiz", "invited")

    def is_accepted(self) -> bool:
        return self.accepted_at is not None

    def can_be_accepted_by(self, user_id: UUID) -> bool:
        return str(self.invited_id) == str(user_id)

    def accept(self) -> None:
        self.accepted_at = timezone.now()

    def get_formatted_invited_at(self) -> str:
        return self.invited_at.strftime(self.__UTC_DATETIME_FORMAT)
