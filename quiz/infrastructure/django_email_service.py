import smtplib
import socket
from logging import getLogger

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from quiz.domain.invitation.email_service import EmailService
from quiz.domain.invitation.invitation import Invitation
from quiz.infrastructure.email_delivery_exception import EmailDeliveryException


class DjangoEmailService(EmailService):
    def __init__(self):
        self.__logger = getLogger(__name__)

    def send_invitation_email(self, invitation: Invitation, invitation_acceptance_link: str) -> None:
        self.__logger.info(f"Sending email to {invitation.invited.email}")

        context = {
            "participant_name": invitation.invited.first_name or invitation.invited.username,
            "quiz_title": invitation.quiz.title,
            "quiz_description": invitation.quiz.description,
            "inviter_name": invitation.inviter.first_name or invitation.inviter.username,
            "invitation_acceptance_link": invitation_acceptance_link,
        }

        html_message = render_to_string("invitation_email.html", context)
        plain_message = render_to_string("invitation_email.txt", context)

        try:
            send_mail(
                subject=f"You're invited to take the quiz: {invitation.quiz.title}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.invited.email],
                html_message=html_message,
                fail_silently=False,
            )
        except (
            smtplib.SMTPException,
            socket.error,
            socket.timeout,
            ConnectionError,
            OSError,
        ) as e:
            self.__logger.error(f"Failed to send email to {invitation.invited.email}: {e}")
            raise EmailDeliveryException(e) from e

        self.__logger.info(f"Email sent successfully to {invitation.invited.email}")
