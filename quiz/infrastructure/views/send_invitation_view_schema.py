from voluptuous import Required, Schema, Invalid, All, Optional
import re


def validate_email(value: str | None) -> str:
    if value is None or value.strip() == "":
        raise Invalid("Email must not be empty")

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, value.strip()):
        raise Invalid("Invalid email format")

    return value.strip()


send_invitation_view_schema = Schema(
    {
        Required("participant_email"): All(str, validate_email),
    }
)
