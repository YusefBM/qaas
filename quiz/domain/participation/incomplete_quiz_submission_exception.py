class IncompleteQuizSubmissionException(Exception):
    def __init__(self, expected_answers: int, received_answers: int):
        self.expected_answers = expected_answers
        self.received_answers = received_answers
        self.message = (
            f"All questions must be answered to complete the quiz. "
            f"Expected {expected_answers} answers, but received {received_answers}."
        )
        super().__init__(self.message)
