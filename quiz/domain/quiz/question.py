from django.db import models

from quiz.domain.quiz.quiz import Quiz


class Question(models.Model):
    REQUIRED_NUMBER_OF_ANSWERS = 3

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["quiz", "order"]
