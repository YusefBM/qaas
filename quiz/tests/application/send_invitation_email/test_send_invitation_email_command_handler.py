import unittest
from unittest.mock import Mock
from uuid import UUID

from quiz.application.send_invitation_email.send_invitation_email_command import SendInvitationEmailCommand
from quiz.application.send_invitation_email.send_invitation_email_command_handler import (
    SendInvitationEmailCommandHandler,
)
from quiz.domain.invitation.email_service import EmailService
from quiz.domain.invitation.invitation import Invitation
from quiz.domain.invitation.invitation_not_found_exception import InvitationNotFoundException
from quiz.domain.invitation.invitation_related_attribute import InvitationRelatedAttribute
from quiz.domain.invitation.invitation_repository import InvitationRepository


class TestSendInvitationEmailCommandHandler(unittest.TestCase):
    def setUp(self):
        self.invitation_repository_mock = Mock(spec=InvitationRepository)
        self.email_service_mock = Mock(spec=EmailService)

        self.handler = SendInvitationEmailCommandHandler(
            invitation_repository=self.invitation_repository_mock, email_service=self.email_service_mock
        )

        self.invitation_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.invitation_acceptance_link = "https://example.com/invitations/12345678-1234-5678-9abc-123456789abc/accept"

        self.command = SendInvitationEmailCommand(
            invitation_id=self.invitation_id, invitation_acceptance_link=self.invitation_acceptance_link
        )

    def test_handle_success(self):
        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id

        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        result = self.handler.handle(self.command)

        self.assertIsNone(result)

        self.invitation_repository_mock.find_or_fail_by_id.assert_called_once_with(
            self.invitation_id,
            related_attributes=[
                InvitationRelatedAttribute.QUIZ,
                InvitationRelatedAttribute.INVITED,
                InvitationRelatedAttribute.INVITER,
            ],
        )
        self.email_service_mock.send_invitation_email.assert_called_once_with(
            mock_invitation, self.invitation_acceptance_link
        )

    def test_handle_invitation_not_found_raises_exception(self):
        self.invitation_repository_mock.find_or_fail_by_id.side_effect = InvitationNotFoundException(self.invitation_id)

        with self.assertRaises(InvitationNotFoundException) as context:
            self.handler.handle(self.command)

        self.assertEqual(context.exception.invitation_id, UUID("12345678-1234-5678-9abc-123456789abc"))
        self.email_service_mock.send_invitation_email.assert_not_called()

    def test_handle_different_invitation_id(self):
        different_invitation_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        different_link = "https://example.com/invitations/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/accept"
        different_command = SendInvitationEmailCommand(
            invitation_id=different_invitation_id, invitation_acceptance_link=different_link
        )

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = different_invitation_id

        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        result = self.handler.handle(different_command)

        self.assertIsNone(result)
        self.invitation_repository_mock.find_or_fail_by_id.assert_called_once_with(
            different_invitation_id,
            related_attributes=[
                InvitationRelatedAttribute.QUIZ,
                InvitationRelatedAttribute.INVITED,
                InvitationRelatedAttribute.INVITER,
            ],
        )
        self.email_service_mock.send_invitation_email.assert_called_once_with(mock_invitation, different_link)

    def test_handle_production_link_format(self):
        production_link = "https://production.quizapp.com/invitations/12345678-1234-5678-9abc-123456789abc/accept"
        production_command = SendInvitationEmailCommand(
            invitation_id=self.invitation_id, invitation_acceptance_link=production_link
        )

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id

        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        result = self.handler.handle(production_command)

        self.assertIsNone(result)
        self.email_service_mock.send_invitation_email.assert_called_once_with(mock_invitation, production_link)

    def test_handle_localhost_link_format(self):
        localhost_link = "http://localhost:8000/invitations/12345678-1234-5678-9abc-123456789abc/accept"
        localhost_command = SendInvitationEmailCommand(
            invitation_id=self.invitation_id, invitation_acceptance_link=localhost_link
        )

        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id

        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        result = self.handler.handle(localhost_command)

        self.assertIsNone(result)
        self.email_service_mock.send_invitation_email.assert_called_once_with(mock_invitation, localhost_link)

    def test_handle_repository_called_with_all_related_attributes(self):
        mock_invitation = Mock(spec=Invitation)
        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        self.handler.handle(self.command)

        args, kwargs = self.invitation_repository_mock.find_or_fail_by_id.call_args
        self.assertEqual(args[0], self.invitation_id)

        related_attributes = kwargs["related_attributes"]
        self.assertIn(InvitationRelatedAttribute.QUIZ, related_attributes)
        self.assertIn(InvitationRelatedAttribute.INVITED, related_attributes)
        self.assertIn(InvitationRelatedAttribute.INVITER, related_attributes)
        self.assertEqual(len(related_attributes), 3)

    def test_handle_email_service_receives_correct_parameters(self):
        mock_invitation = Mock(spec=Invitation)
        mock_invitation.id = self.invitation_id

        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation

        self.handler.handle(self.command)

        args, kwargs = self.email_service_mock.send_invitation_email.call_args
        self.assertEqual(args[0], mock_invitation)
        self.assertEqual(args[1], self.invitation_acceptance_link)
        self.assertEqual(len(args), 2)
        self.assertEqual(len(kwargs), 0)

    def test_handle_multiple_invitations_sequential(self):
        invitation_id_1 = UUID("11111111-1111-1111-1111-111111111111")
        invitation_id_2 = UUID("22222222-2222-2222-2222-222222222222")

        mock_invitation_1 = Mock(spec=Invitation)
        mock_invitation_1.id = invitation_id_1
        mock_invitation_2 = Mock(spec=Invitation)
        mock_invitation_2.id = invitation_id_2

        command_1 = SendInvitationEmailCommand(
            invitation_id=invitation_id_1,
            invitation_acceptance_link="https://example.com/invitations/11111111-1111-1111-1111-111111111111/accept",
        )
        command_2 = SendInvitationEmailCommand(
            invitation_id=invitation_id_2,
            invitation_acceptance_link="https://example.com/invitations/22222222-2222-2222-2222-222222222222/accept",
        )

        self.invitation_repository_mock.find_or_fail_by_id.side_effect = [mock_invitation_1, mock_invitation_2]

        self.handler.handle(command_1)
        self.handler.handle(command_2)

        self.assertEqual(self.invitation_repository_mock.find_or_fail_by_id.call_count, 2)
        self.assertEqual(self.email_service_mock.send_invitation_email.call_count, 2)

    def test_handle_email_service_error_propagates(self):
        mock_invitation = Mock(spec=Invitation)
        self.invitation_repository_mock.find_or_fail_by_id.return_value = mock_invitation
        self.email_service_mock.send_invitation_email.side_effect = Exception("Email service unavailable")

        with self.assertRaises(Exception) as context:
            self.handler.handle(self.command)

        self.assertEqual(str(context.exception), "Email service unavailable")
        self.invitation_repository_mock.find_or_fail_by_id.assert_called_once()
        self.email_service_mock.send_invitation_email.assert_called_once()
