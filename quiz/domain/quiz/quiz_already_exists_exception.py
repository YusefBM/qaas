class QuizAlreadyExistsException(Exception):
    def __init__(self, title: str, creator_id: str) -> None:
        self.title = title
        self.creator_id = creator_id
        super().__init__(f"Quiz with title '{self.title}' already exists for the user '{creator_id}'")
