import smtplib
import socket
import unittest
from unittest.mock import Mock, patch

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.quiz.quiz import Quiz
from quiz.infrastructure.django_email_service import DjangoEmailService
from quiz.infrastructure.email_delivery_exception import EmailDeliveryException
from user.domain.user import User


class TestDjangoEmailService(unittest.TestCase):
    def setUp(self):
        self.email_service = DjangoEmailService()

        self.mock_quiz = Mock(spec=Quiz)
        self.mock_quiz.title = "JavaScript Fundamentals"
        self.mock_quiz.description = "Learn the basics of JavaScript programming"

        self.mock_inviter = Mock(spec=User)
        self.mock_inviter.first_name = "John"
        self.mock_inviter.username = "john_teacher"

        self.mock_invited = Mock(spec=User)
        self.mock_invited.first_name = "Alice"
        self.mock_invited.username = "alice_student"
        self.mock_invited.email = "alice@student.com"

        self.mock_invitation = Mock(spec=Invitation)
        self.mock_invitation.quiz = self.mock_quiz
        self.mock_invitation.inviter = self.mock_inviter
        self.mock_invitation.invited = self.mock_invited

        self.invitation_link = "https://quiz.app/accept/12345678-abcd-efgh"

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_success_with_first_names(self, mock_settings, mock_render, mock_send_mail):
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        expected_context = {
            "participant_name": "Alice",
            "quiz_title": "JavaScript Fundamentals",
            "quiz_description": "Learn the basics of JavaScript programming",
            "inviter_name": "John",
            "invitation_acceptance_link": self.invitation_link,
        }

        self.assertEqual(mock_render.call_count, 2)
        mock_render.assert_any_call("invitation_email.html", expected_context)
        mock_render.assert_any_call("invitation_email.txt", expected_context)

        mock_send_mail.assert_called_once_with(
            subject="You're invited to take the quiz: JavaScript Fundamentals",
            message="Plain text email content",
            from_email="noreply@quiz.app",
            recipient_list=["alice@student.com"],
            html_message="<html>HTML Email Content</html>",
            fail_silently=False,
        )

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_success_with_usernames_when_no_first_names(
        self, mock_settings, mock_render, mock_send_mail
    ):
        self.mock_inviter.first_name = None
        self.mock_invited.first_name = None

        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        expected_context = {
            "participant_name": "alice_student",
            "quiz_title": "JavaScript Fundamentals",
            "quiz_description": "Learn the basics of JavaScript programming",
            "inviter_name": "john_teacher",
            "invitation_acceptance_link": self.invitation_link,
        }

        mock_render.assert_any_call("invitation_email.html", expected_context)
        mock_render.assert_any_call("invitation_email.txt", expected_context)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_success_with_empty_first_names(self, mock_settings, mock_render, mock_send_mail):
        self.mock_inviter.first_name = ""
        self.mock_invited.first_name = ""

        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        expected_context = {
            "participant_name": "alice_student",
            "quiz_title": "JavaScript Fundamentals",
            "quiz_description": "Learn the basics of JavaScript programming",
            "inviter_name": "john_teacher",
            "invitation_acceptance_link": self.invitation_link,
        }

        mock_render.assert_any_call("invitation_email.html", expected_context)
        mock_render.assert_any_call("invitation_email.txt", expected_context)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_raises_email_delivery_exception_on_smtp_exception(
        self, mock_settings, mock_render, mock_send_mail
    ):
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        smtp_error = smtplib.SMTPException("SMTP server error")
        mock_send_mail.side_effect = smtp_error

        with self.assertRaises(EmailDeliveryException) as context:
            self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        self.assertEqual(context.exception.__cause__, smtp_error)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_raises_email_delivery_exception_on_socket_error(
        self, mock_settings, mock_render, mock_send_mail
    ):
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        socket_error = socket.error("Connection failed")
        mock_send_mail.side_effect = socket_error

        with self.assertRaises(EmailDeliveryException) as context:
            self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        self.assertEqual(context.exception.__cause__, socket_error)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_raises_email_delivery_exception_on_socket_timeout(
        self, mock_settings, mock_render, mock_send_mail
    ):
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        timeout_error = socket.timeout("Timeout occurred")
        mock_send_mail.side_effect = timeout_error

        with self.assertRaises(EmailDeliveryException) as context:
            self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        self.assertEqual(context.exception.__cause__, timeout_error)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_raises_email_delivery_exception_on_connection_error(
        self, mock_settings, mock_render, mock_send_mail
    ):
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        connection_error = ConnectionError("Connection refused")
        mock_send_mail.side_effect = connection_error

        with self.assertRaises(EmailDeliveryException) as context:
            self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        self.assertEqual(context.exception.__cause__, connection_error)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_raises_email_delivery_exception_on_os_error(
        self, mock_settings, mock_render, mock_send_mail
    ):
        mock_settings.DEFAULT_FROM_EMAIL = "noreply@quiz.app"
        mock_render.side_effect = ["<html>HTML Email Content</html>", "Plain text email content"]

        os_error = OSError("OS level error")
        mock_send_mail.side_effect = os_error

        with self.assertRaises(EmailDeliveryException) as context:
            self.email_service.send_invitation_email(self.mock_invitation, self.invitation_link)

        self.assertEqual(context.exception.__cause__, os_error)

    @patch("quiz.infrastructure.django_email_service.send_mail")
    @patch("quiz.infrastructure.django_email_service.render_to_string")
    @patch("quiz.infrastructure.django_email_service.settings")
    def test_send_invitation_email_different_quiz_and_user_data(self, mock_settings, mock_render, mock_send_mail):
        different_quiz = Mock(spec=Quiz)
        different_quiz.title = "Python Advanced"
        different_quiz.description = "Advanced Python concepts"

        different_inviter = Mock(spec=User)
        different_inviter.first_name = "Bob"
        different_inviter.username = "bob_instructor"

        different_invited = Mock(spec=User)
        different_invited.first_name = "Charlie"
        different_invited.username = "charlie_dev"
        different_invited.email = "charlie@developer.com"

        different_invitation = Mock(spec=Invitation)
        different_invitation.quiz = different_quiz
        different_invitation.inviter = different_inviter
        different_invitation.invited = different_invited

        different_link = "https://quiz.app/accept/different-link"

        mock_settings.DEFAULT_FROM_EMAIL = "system@quiz.app"
        mock_render.side_effect = ["<html>Different HTML Content</html>", "Different plain text content"]

        self.email_service.send_invitation_email(different_invitation, different_link)

        expected_context = {
            "participant_name": "Charlie",
            "quiz_title": "Python Advanced",
            "quiz_description": "Advanced Python concepts",
            "inviter_name": "Bob",
            "invitation_acceptance_link": different_link,
        }

        mock_render.assert_any_call("invitation_email.html", expected_context)
        mock_render.assert_any_call("invitation_email.txt", expected_context)

        mock_send_mail.assert_called_once_with(
            subject="You're invited to take the quiz: Python Advanced",
            message="Different plain text content",
            from_email="system@quiz.app",
            recipient_list=["charlie@developer.com"],
            html_message="<html>Different HTML Content</html>",
            fail_silently=False,
        )
