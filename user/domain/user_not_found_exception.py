class UserNotFoundException(Exception):
    def __init__(self, user_id: str | None = None, user_email: str | None = None) -> None:
        self.user_id = user_id
        self.user_email = user_email
        if user_id is not None:
            error_msg = f"User with id '{self.user_id}' not found"
        else:
            error_msg = f"User with email '{self.user_email}' not found"
        super().__init__(error_msg)
