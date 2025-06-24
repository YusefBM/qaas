from uuid import UUID


class InvalidQuizTitleLengthException(Exception):
    def __init__(self, quiz_id: UUID, title: str, max_length: int):
        self.quiz_id = quiz_id
        self.title = title
        self.max_length = max_length
        super().__init__(
            f"Quiz {self.quiz_id} title exceeds maximum length of {max_length} characters (current length: {len(title)})"
        )
