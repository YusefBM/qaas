from typing import Optional
from uuid import UUID
from django.utils import timezone
from django.db import IntegrityError

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_already_exists_exception import InvitationAlreadyExistsException
from quiz.domain.invitation.invitation_not_found_exception import InvitationNotFoundException
from quiz.domain.invitation.invitation_related_attribute import InvitationRelatedAttribute
from quiz.domain.invitation.invitation_repository import InvitationRepository


class DbInvitationRepository(InvitationRepository):
    __UNIQUE_CONSTRAINT_QUIZ_AND_PARTICIPANT = "quiz_invitation_quiz_id_invited_id"

    def find_or_fail_by_id(
        self, invitation_id: UUID, related_attributes: list[InvitationRelatedAttribute] | None = None
    ) -> Invitation:
        try:
            queryset = Invitation.objects.filter(id=invitation_id)
            if related_attributes is not None:
                queryset = queryset.select_related(*related_attributes)

            return queryset.get()
        except Invitation.DoesNotExist:
            raise InvitationNotFoundException(invitation_id)

    def find_active_invitation(self, quiz_id: UUID, participant_id: UUID) -> Optional[Invitation]:
        try:
            return Invitation.objects.select_related("quiz", "invited").get(
                quiz_id=quiz_id, participant_id=participant_id, accepted_at__isnull=True
            )
        except Invitation.DoesNotExist:
            return None

    def save(self, invitation: Invitation) -> None:
        try:
            invitation.save()
        except IntegrityError as exc:
            if self._is_unique_constraint_violation(exc):
                raise InvitationAlreadyExistsException(
                    quiz_id=str(invitation.quiz.id), participant_id=str(invitation.invited.id)
                )
            raise exc

    def exists_by_quiz_and_invited(self, quiz_id: UUID, invited_id: UUID) -> bool:
        return Invitation.objects.filter(quiz_id=quiz_id, invited_id=invited_id).exists()

    def _is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_QUIZ_AND_PARTICIPANT in exc.__cause__.diag.constraint_name
