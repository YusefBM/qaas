import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.application.send_invitation_email.send_invitation_email_command import SendInvitationEmailCommand
from quiz.infrastructure.send_invitation_email_task import send_invitation_email_task


class TestSendInvitationEmailTask(unittest.TestCase):
    def setUp(self):
        self.invitation_id_str = "12345678-1234-5678-9abc-123456789abc"
        self.invitation_id_uuid = UUID(self.invitation_id_str)
        self.invitation_link = "https://quiz.app/accept/invitation/12345678-1234-5678-9abc-123456789abc"

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_success(self, mock_factory):
        mock_handler = Mock()
        mock_factory.create.return_value = mock_handler

        send_invitation_email_task(self.invitation_id_str, self.invitation_link)

        mock_factory.create.assert_called_once()
        mock_handler.handle.assert_called_once()

        call_args = mock_handler.handle.call_args[0][0]
        self.assertIsInstance(call_args, SendInvitationEmailCommand)
        self.assertEqual(call_args.invitation_id, self.invitation_id_uuid)
        self.assertEqual(call_args.invitation_acceptance_link, self.invitation_link)

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_converts_string_to_uuid(self, mock_factory):
        mock_handler = Mock()
        mock_factory.create.return_value = mock_handler

        different_id_str = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        different_id_uuid = UUID(different_id_str)

        send_invitation_email_task(different_id_str, self.invitation_link)

        call_args = mock_handler.handle.call_args[0][0]
        self.assertEqual(call_args.invitation_id, different_id_uuid)

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_with_different_links(self, mock_factory):
        mock_handler = Mock()
        mock_factory.create.return_value = mock_handler

        test_links = [
            "https://example.com/accept/123",
            "http://localhost:8000/invitation/accept",
            "https://app.quiz.com/invitations/12345/accept",
        ]

        for link in test_links:
            with self.subTest(link=link):
                send_invitation_email_task(self.invitation_id_str, link)

                call_args = mock_handler.handle.call_args[0][0]
                self.assertEqual(call_args.invitation_acceptance_link, link)

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_creates_new_handler_each_time(self, mock_factory):
        mock_handler1 = Mock()
        mock_handler2 = Mock()
        mock_factory.create.side_effect = [mock_handler1, mock_handler2]

        send_invitation_email_task(self.invitation_id_str, self.invitation_link)
        send_invitation_email_task(self.invitation_id_str, self.invitation_link)

        self.assertEqual(mock_factory.create.call_count, 2)
        mock_handler1.handle.assert_called_once()
        mock_handler2.handle.assert_called_once()

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_propagates_handler_exception(self, mock_factory):
        mock_handler = Mock()
        mock_handler.handle.side_effect = Exception("Handler failed")
        mock_factory.create.return_value = mock_handler

        with self.assertRaises(Exception) as context:
            send_invitation_email_task(self.invitation_id_str, self.invitation_link)

        self.assertEqual(str(context.exception), "Handler failed")

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_propagates_factory_exception(self, mock_factory):
        mock_factory.create.side_effect = Exception("Factory failed")

        with self.assertRaises(Exception) as context:
            send_invitation_email_task(self.invitation_id_str, self.invitation_link)

        self.assertEqual(str(context.exception), "Factory failed")

    def test_send_invitation_email_task_raises_value_error_on_invalid_uuid(self):
        invalid_uuid_str = "invalid-uuid-string"

        with self.assertRaises(ValueError):
            send_invitation_email_task(invalid_uuid_str, self.invitation_link)

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_with_empty_link(self, mock_factory):
        mock_handler = Mock()
        mock_factory.create.return_value = mock_handler

        empty_link = ""

        send_invitation_email_task(self.invitation_id_str, empty_link)

        call_args = mock_handler.handle.call_args[0][0]
        self.assertEqual(call_args.invitation_acceptance_link, empty_link)

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_with_complex_link(self, mock_factory):
        mock_handler = Mock()
        mock_factory.create.return_value = mock_handler

        complex_link = "https://quiz.app/accept?token=abc123&redirect=/dashboard&utm_source=email"

        send_invitation_email_task(self.invitation_id_str, complex_link)

        call_args = mock_handler.handle.call_args[0][0]
        self.assertEqual(call_args.invitation_acceptance_link, complex_link)

    @patch("quiz.infrastructure.send_invitation_email_task.SendInvitationEmailCommandHandlerFactory")
    def test_send_invitation_email_task_command_creation_with_exact_parameters(self, mock_factory):
        mock_handler = Mock()
        mock_factory.create.return_value = mock_handler

        send_invitation_email_task(self.invitation_id_str, self.invitation_link)

        call_args = mock_handler.handle.call_args[0][0]
        self.assertIsInstance(call_args, SendInvitationEmailCommand)
        self.assertTrue(hasattr(call_args, "invitation_id"))
        self.assertTrue(hasattr(call_args, "invitation_acceptance_link"))
        self.assertEqual(len(call_args.__dict__), 2)
