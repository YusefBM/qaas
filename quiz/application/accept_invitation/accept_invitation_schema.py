from uuid import UUID

from voluptuous import Required, Schema, Invalid


def validate_uuid(value) -> UUID:
    if value is None:
        raise Invalid("UUID cannot be None")

    if isinstance(value, UUID):
        return value

    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        raise Invalid("Invalid UUID format")


accept_invitation_schema = Schema(
    {
        Required("invitation_id"): validate_uuid,
        Required("user_id"): validate_uuid,
    }
)
