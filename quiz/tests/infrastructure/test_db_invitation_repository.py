import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from django.db import IntegrityError

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_already_exists_exception import InvitationAlreadyExistsException
from quiz.domain.invitation.invitation_not_found_exception import InvitationNotFoundException
from quiz.domain.invitation.invitation_related_attribute import InvitationRelatedAttribute
from quiz.domain.quiz.quiz import Quiz
from quiz.infrastructure.db_invitation_repository import DbInvitationRepository
from user.domain.user import User


class TestDbInvitationRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DbInvitationRepository()
        self.invitation_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.quiz_id = UUID("87654321-4321-8765-cba9-987654321098")
        self.participant_id = UUID("11111111-2222-3333-4444-555555555555")

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_or_fail_by_id_success_without_related_attributes(self, mock_objects):
        expected_invitation = Mock(spec=Invitation)
        expected_invitation.id = self.invitation_id

        mock_queryset = Mock()
        mock_queryset.get.return_value = expected_invitation
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_or_fail_by_id(self.invitation_id)

        self.assertEqual(result, expected_invitation)
        mock_objects.filter.assert_called_once_with(id=self.invitation_id)
        mock_queryset.get.assert_called_once()

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_or_fail_by_id_success_with_related_attributes(self, mock_objects):
        expected_invitation = Mock(spec=Invitation)
        expected_invitation.id = self.invitation_id

        related_attributes = [InvitationRelatedAttribute.QUIZ, InvitationRelatedAttribute.INVITED]

        mock_queryset = Mock()
        mock_select_related_queryset = Mock()
        mock_queryset.select_related.return_value = mock_select_related_queryset
        mock_select_related_queryset.get.return_value = expected_invitation
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_or_fail_by_id(self.invitation_id, related_attributes)

        self.assertEqual(result, expected_invitation)
        mock_objects.filter.assert_called_once_with(id=self.invitation_id)
        mock_queryset.select_related.assert_called_once_with(*related_attributes)
        mock_select_related_queryset.get.assert_called_once()

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_or_fail_by_id_raises_invitation_not_found_exception(self, mock_objects):
        mock_queryset = Mock()
        mock_queryset.get.side_effect = Invitation.DoesNotExist
        mock_objects.filter.return_value = mock_queryset

        with self.assertRaises(InvitationNotFoundException) as context:
            self.repository.find_or_fail_by_id(self.invitation_id)

        self.assertEqual(context.exception.invitation_id, self.invitation_id)

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_active_invitation_success(self, mock_objects):
        expected_invitation = Mock(spec=Invitation)
        expected_invitation.quiz_id = self.quiz_id
        expected_invitation.participant_id = self.participant_id

        mock_select_related_queryset = Mock()
        mock_select_related_queryset.get.return_value = expected_invitation
        mock_objects.select_related.return_value = mock_select_related_queryset

        result = self.repository.find_active_invitation(self.quiz_id, self.participant_id)

        self.assertEqual(result, expected_invitation)
        mock_objects.select_related.assert_called_once_with("quiz", "invited")
        mock_select_related_queryset.get.assert_called_once_with(
            quiz_id=self.quiz_id, participant_id=self.participant_id, accepted_at__isnull=True
        )

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_active_invitation_returns_none_when_not_found(self, mock_objects):
        mock_select_related_queryset = Mock()
        mock_select_related_queryset.get.side_effect = Invitation.DoesNotExist
        mock_objects.select_related.return_value = mock_select_related_queryset

        result = self.repository.find_active_invitation(self.quiz_id, self.participant_id)

        self.assertIsNone(result)

    def test_save_success(self):
        invitation = Mock(spec=Invitation)
        invitation.quiz = Mock(spec=Quiz)
        invitation.quiz.id = self.quiz_id
        invitation.invited = Mock(spec=User)
        invitation.invited.id = self.participant_id

        self.repository.save(invitation)

        invitation.save.assert_called_once()

    def test_save_raises_invitation_already_exists_exception_on_unique_constraint_violation(self):
        invitation = Mock(spec=Invitation)
        invitation.quiz = Mock(spec=Quiz)
        invitation.quiz.id = self.quiz_id
        invitation.invited = Mock(spec=User)
        invitation.invited.id = self.participant_id

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_invitation_quiz_id_invited_id"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        invitation.save.side_effect = integrity_error

        with self.assertRaises(InvitationAlreadyExistsException) as context:
            self.repository.save(invitation)

        self.assertEqual(context.exception.quiz_id, str(self.quiz_id))
        self.assertEqual(context.exception.participant_id, str(self.participant_id))

    def test_save_raises_original_integrity_error_on_other_constraint_violation(self):
        invitation = Mock(spec=Invitation)

        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "some_other_constraint"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Other database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        invitation.save.side_effect = integrity_error

        with self.assertRaises(IntegrityError):
            self.repository.save(invitation)

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_exists_by_quiz_and_participant_returns_true_when_exists(self, mock_objects):
        mock_objects.filter.return_value.exists.return_value = True

        result = self.repository.exists_by_quiz_and_invited(self.quiz_id, self.participant_id)

        self.assertTrue(result)
        mock_objects.filter.assert_called_once_with(quiz_id=self.quiz_id, invited_id=self.participant_id)

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_exists_by_quiz_and_participant_returns_false_when_not_exists(self, mock_objects):
        mock_objects.filter.return_value.exists.return_value = False

        result = self.repository.exists_by_quiz_and_invited(self.quiz_id, self.participant_id)

        self.assertFalse(result)
        mock_objects.filter.assert_called_once_with(quiz_id=self.quiz_id, invited_id=self.participant_id)

    @patch("quiz.domain.invitation.invitation.Invitation.objects")
    def test_find_or_fail_by_id_with_empty_related_attributes_list(self, mock_objects):
        expected_invitation = Mock(spec=Invitation)
        expected_invitation.id = self.invitation_id

        mock_queryset = Mock()
        mock_select_related_queryset = Mock()
        mock_queryset.select_related.return_value = mock_select_related_queryset
        mock_select_related_queryset.get.return_value = expected_invitation
        mock_objects.filter.return_value = mock_queryset

        result = self.repository.find_or_fail_by_id(self.invitation_id, [])

        self.assertEqual(result, expected_invitation)
        mock_queryset.select_related.assert_called_once_with()

    def test_is_unique_constraint_violation_returns_true_for_quiz_participant_constraint(self):
        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "quiz_invitation_quiz_id_invited_id"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("UNIQUE constraint failed")
        integrity_error.__cause__ = mock_cause

        result = self.repository._is_unique_constraint_violation(integrity_error)

        self.assertTrue(result)

    def test_is_unique_constraint_violation_returns_false_for_other_constraints(self):
        mock_constraint_diag = Mock()
        mock_constraint_diag.constraint_name = "some_other_constraint"

        class MockCause(Exception):
            def __init__(self):
                super().__init__("Other database constraint violation")
                self.diag = mock_constraint_diag

        mock_cause = MockCause()

        integrity_error = IntegrityError("Other constraint failed")
        integrity_error.__cause__ = mock_cause

        result = self.repository._is_unique_constraint_violation(integrity_error)

        self.assertFalse(result)
