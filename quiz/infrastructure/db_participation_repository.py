from uuid import UUID

from django.db import IntegrityError

from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_already_exists_exception import ParticipationAlreadyExistsException
from quiz.domain.participation.participation_not_found_for_quiz_and_participant_exception import (
    ParticipationNotFoundForQuizAndParticipantException,
)
from quiz.domain.participation.participation_related_attribute import ParticipationRelatedAttribute
from quiz.domain.participation.participation_repository import ParticipationRepository


class DbParticipationRepository(ParticipationRepository):
    __UNIQUE_CONSTRAINT_QUIZ_AND_PARTICIPANT = "quiz_participation_quiz_id_participant_id_ef6ab5ef_uniq"

    def find_all_by_user_id(
        self, user_id: UUID, related_attributes: list[ParticipationRelatedAttribute] | None = None
    ) -> list[Participation]:
        queryset = Participation.objects.filter(participant_id=user_id)
        if related_attributes is not None:
            queryset = queryset.select_related(*related_attributes)

        return list(queryset.order_by("-quiz__created_at"))

    def find_or_fail_by_quiz_and_participant(self, quiz_id: UUID, participant_id: UUID) -> Participation:
        try:
            return Participation.objects.select_related("quiz", "participant", "invitation").get(
                quiz_id=quiz_id, participant_id=participant_id
            )
        except Participation.DoesNotExist as e:
            raise ParticipationNotFoundForQuizAndParticipantException(quiz_id, participant_id) from e

    def save(self, participation: Participation) -> None:
        try:
            participation.save()
        except IntegrityError as exc:
            if self.__is_unique_constraint_violation(exc):
                raise ParticipationAlreadyExistsException(
                    quiz_id=str(participation.quiz.id), participant_id=str(participation.participant.id)
                ) from exc
            raise exc

    def exists_by_quiz_and_participant(self, quiz_id: UUID, participant_id: UUID) -> bool:
        return Participation.objects.filter(quiz_id=quiz_id, participant_id=participant_id).exists()

    def __is_unique_constraint_violation(self, exc: IntegrityError) -> bool:
        return self.__UNIQUE_CONSTRAINT_QUIZ_AND_PARTICIPANT in exc.__cause__.diag.constraint_name
