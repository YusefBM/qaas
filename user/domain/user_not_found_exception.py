class UserNotFoundException(Exception):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User with id '{self.user_id}' not found")
