from django.db import models
from uuid_utils.compat import uuid7

from quiz.domain.quiz.empty_quiz_title_exception import EmptyQuizTitleException
from quiz.domain.quiz.invalid_quiz_title_length_exception import InvalidQuizTitleLengthException
from user.domain.user import User


class Quiz(models.Model):
    __UTC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    __MAX_TITLE_LENGTH = 200

    id = models.UUIDField(primary_key=True, default=uuid7)
    title = models.CharField(max_length=__MAX_TITLE_LENGTH)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="quizzes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["title", "creator"]

    def __init__(self, *args, **kwargs):
        title = kwargs.get("title")
        if title is not None:
            self.__validate_title(title)

        super().__init__(*args, **kwargs)

    def __validate_title(self, title: str) -> None:
        if not title or title.strip() == "":
            raise EmptyQuizTitleException(self.id)

        if len(title) > self.__MAX_TITLE_LENGTH:
            raise InvalidQuizTitleLengthException(self.id, title, self.__MAX_TITLE_LENGTH)

    def __str__(self):
        return f"{self.title}"

    def get_formatted_created_at(self) -> str:
        return self.created_at.strftime(self.__UTC_DATETIME_FORMAT)

    @property
    def total_questions(self) -> int:
        return self.questions.count()

    @property
    def total_participants(self) -> int:
        return self.participations.count() if hasattr(self, "participations") else 0
