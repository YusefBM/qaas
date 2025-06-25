import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from django.db import IntegrityError

from quiz.domain.participation.participation import Participation
from quiz.domain.participation.participation_already_exists_exception import ParticipationAlreadyExistsException
from quiz.domain.participation.participation_not_found_for_quiz_and_participant_exception import (
    ParticipationNotFoundForQuizAndParticipantException,
)
from quiz.domain.participation.participation_related_attribute import ParticipationRelatedAttribute
from quiz.domain.quiz.quiz import Quiz
from quiz.infrastructure.db_participation_repository import DbParticipationRepository
from user.domain.user import User


class TestDbParticipationRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbParticipationRepository()
        self.user_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.quiz_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participant_id = UUID("11111111-2222-3333-4444-555555555555")

        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.id = self.quiz_id
        self.mock_quiz.title = "JavaScript Quiz"

        self.mock_participant = Mock(spec=User)
        self.mock_participant.id = self.participant_id
        self.mock_participant.email = "participant@test.com"

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_all_by_user_id_without_related_attributes(self, mock_objects):
        participation1 = Mock(spec=Participation)
        participation1.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        participation2 = Mock(spec=Participation)
        participation2.id = UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff")

        mock_queryset = Mock()
        mock_queryset.order_by.return_value = [participation1, participation2]
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_all_by_user_id(self.user_id)

        self.assertEqual(result, [participation1, participation2])
        mock_objects.filter.assert_called_once_with(participant_id=self.user_id)
        mock_queryset.order_by.assert_called_once_with("-quiz__created_at")

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_all_by_user_id_with_related_attributes(self, mock_objects):
        participation1 = Mock(spec=Participation)
        participation1.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        related_attributes = [ParticipationRelatedAttribute.QUIZ, ParticipationRelatedAttribute.PARTICIPANT]

        mock_queryset = Mock()
        mock_select_related_queryset = Mock()
        mock_queryset.select_related.return_value = mock_select_related_queryset
        mock_select_related_queryset.order_by.return_value = [participation1]
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_all_by_user_id(self.user_id, related_attributes)

        self.assertEqual(result, [participation1])
        mock_objects.filter.assert_called_once_with(participant_id=self.user_id)
        mock_queryset.select_related.assert_called_once_with(*related_attributes)
        mock_select_related_queryset.order_by.assert_called_once_with("-quiz__created_at")

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_all_by_user_id_returns_empty_list_when_no_participations(self, mock_objects):
        mock_queryset = Mock()
        mock_queryset.order_by.return_value = []
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_all_by_user_id(self.user_id)

        self.assertEqual(result, [])

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_or_fail_by_quiz_and_participant_success(self, mock_objects):
        expected_participation = Mock(spec=Participation)
        expected_participation.quiz = self.mock_quiz
        expected_participation.participant = self.mock_participant

        mock_select_related_queryset = Mock()
        mock_select_related_queryset.get.return_value = expected_participation
        mock_objects.select_related.return_value = mock_select_related_queryset

        result = self.repository.find_or_fail_by_quiz_and_participant(self.quiz_id, self.participant_id)

        self.assertEqual(result, expected_participation)
        mock_objects.select_related.assert_called_once_with("quiz", "participant", "invitation")
        mock_select_related_queryset.get.assert_called_once_with(
            quiz_id=self.quiz_id, participant_id=self.participant_id
        )

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_or_fail_by_quiz_and_participant_raises_participation_not_found_exception(self, mock_objects):
        mock_select_related_queryset = Mock()
        mock_select_related_queryset.get.side_effect = Participation.DoesNotExist
        mock_objects.select_related.return_value = mock_select_related_queryset

        with self.assertRaises(ParticipationNotFoundForQuizAndParticipantException):
            self.repository.find_or_fail_by_quiz_and_participant(self.quiz_id, self.participant_id)

    def test_save_success(self):
        participation = Mock(spec=Participation)
        participation.quiz = self.mock_quiz
        participation.participant = self.mock_participant

        self.repository.save(participation)

        participation.save.assert_called_once()

    def test_save_raises_participation_already_exists_exception_on_unique_constraint_violation(self):
        participation = Mock(spec=Participation)
        participation.quiz = self.mock_quiz
        participation.participant = self.mock_participant

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_participation_quiz_id_participant_id_ef6ab5ef_uniq"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        participation.save.side_effect = integrity_error

        with self.assertRaises(ParticipationAlreadyExistsException) as context:
            self.repository.save(participation)

        self.assertEqual(context.exception.quiz_id, str(self.quiz_id))
        self.assertEqual(context.exception.participant_id, str(self.participant_id))

    def test_save_raises_original_integrity_error_on_other_constraint_violation(self):
        participation = Mock(spec=Participation)

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "some_other_constraint"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Other database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        participation.save.side_effect = integrity_error

        with self.assertRaises(IntegrityError):
            self.repository.save(participation)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_exists_by_quiz_and_participant_returns_true_when_exists(self, mock_objects):
        mock_objects.filter.return_value.exists.return_value = True

        result = self.repository.exists_by_quiz_and_participant(self.quiz_id, self.participant_id)

        self.assertTrue(result)
        mock_objects.filter.assert_called_once_with(quiz_id=self.quiz_id, participant_id=self.participant_id)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_exists_by_quiz_and_participant_returns_false_when_not_exists(self, mock_objects):
        mock_objects.filter.return_value.exists.return_value = False

        result = self.repository.exists_by_quiz_and_participant(self.quiz_id, self.participant_id)

        self.assertFalse(result)
        mock_objects.filter.assert_called_once_with(quiz_id=self.quiz_id, participant_id=self.participant_id)

    @patch("quiz.domain.participation.participation.Participation.objects")
    def test_find_all_by_user_id_with_empty_related_attributes_list(self, mock_objects):
        participation1 = Mock(spec=Participation)
        participation1.id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        mock_queryset = Mock()
        mock_select_related_queryset = Mock()
        mock_queryset.select_related.return_value = mock_select_related_queryset
        mock_select_related_queryset.order_by.return_value = [participation1]
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_all_by_user_id(self.user_id, [])

        self.assertEqual(result, [participation1])
        mock_queryset.select_related.assert_called_once_with()
