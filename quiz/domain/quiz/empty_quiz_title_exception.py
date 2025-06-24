from uuid import UUID


class EmptyQuizTitleException(Exception):
    def __init__(self, quiz_id: UUID):
        self.quiz_id = quiz_id
        super().__init__(f"Quiz {quiz_id} title cannot be empty")
