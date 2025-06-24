import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from quiz.infrastructure.celery_invitacion_sender import CeleryInvitationSender


class TestCeleryInvitationSender(unittest.TestCase):
    def setUp(self):
        self.sender = CeleryInvitationSender()
        self.invitation_id = UUID("12345678-1234-5678-9abc-123456789abc")
        self.invitation_link = "https://quiz.app/accept/invitation/12345678-1234-5678-9abc-123456789abc"

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_calls_celery_task_with_correct_parameters(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        self.sender.send_invitation_email(self.invitation_id, self.invitation_link)

        mock_delay.assert_called_once_with(
            invitation_id=str(self.invitation_id),
            invitation_acceptance_link=self.invitation_link,
        )

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_converts_uuid_to_string(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        different_invitation_id = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        different_link = "https://quiz.app/accept/different"

        self.sender.send_invitation_email(different_invitation_id, different_link)

        mock_delay.assert_called_once_with(
            invitation_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            invitation_acceptance_link=different_link,
        )

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_with_different_links(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        test_cases = [
            "https://example.com/accept/123",
            "http://localhost:8000/invitation/accept",
            "https://app.quiz.com/invitations/12345/accept",
        ]

        for link in test_cases:
            with self.subTest(link=link):
                self.sender.send_invitation_email(self.invitation_id, link)

                mock_delay.assert_called_with(
                    invitation_id=str(self.invitation_id),
                    invitation_acceptance_link=link,
                )

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_with_multiple_invitations(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        invitation_ids = [
            UUID("11111111-2222-3333-4444-555555555555"),
            UUID("66666666-7777-8888-9999-aaaaaaaaaaaa"),
            UUID("bbbbbbbb-cccc-dddd-eeee-ffffffffffff"),
        ]

        for invitation_id in invitation_ids:
            self.sender.send_invitation_email(invitation_id, self.invitation_link)

        self.assertEqual(mock_delay.call_count, 3)

        expected_calls = [
            unittest.mock.call(
                invitation_id=str(invitation_id),
                invitation_acceptance_link=self.invitation_link,
            )
            for invitation_id in invitation_ids
        ]

        mock_delay.assert_has_calls(expected_calls)

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_does_not_wait_for_task_completion(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        result = self.sender.send_invitation_email(self.invitation_id, self.invitation_link)

        self.assertIsNone(result)
        mock_delay.assert_called_once()

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_with_empty_string_link(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        empty_link = ""

        self.sender.send_invitation_email(self.invitation_id, empty_link)

        mock_delay.assert_called_once_with(
            invitation_id=str(self.invitation_id),
            invitation_acceptance_link=empty_link,
        )

    @patch("quiz.infrastructure.celery_invitacion_sender.send_invitation_email_task")
    def test_send_invitation_email_preserves_link_format(self, mock_task):
        mock_delay = Mock()
        mock_task.delay = mock_delay

        complex_link = "https://quiz.app/accept?token=abc123&redirect=/dashboard&utm_source=email"

        self.sender.send_invitation_email(self.invitation_id, complex_link)

        mock_delay.assert_called_once_with(
            invitation_id=str(self.invitation_id),
            invitation_acceptance_link=complex_link,
        )
