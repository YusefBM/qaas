from django.db import models

from quiz.domain.participation.participation import Participation
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.question import Question


class AnswerSubmission(models.Model):
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name="answer_submissions")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_answer = models.ForeignKey(Answer, on_delete=models.PROTECT)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("participation", "question")

    def __str__(self):
        return f"{self.participation.participant.email} - {self.question.text[:30]} - {self.selected_answer.text[:20]}"

    @property
    def is_correct(self) -> bool:
        return self.selected_answer.is_correct
