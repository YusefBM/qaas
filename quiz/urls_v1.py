"""
Quiz API v1 URL Configuration
"""

from django.urls import path

from .infrastructure.views.accept_invitation_view import AcceptInvitationView
from .infrastructure.views.get_creator_quiz_progress_view import GetCreatorQuizProgressView
from .infrastructure.views.get_creator_quizzes_view import GetCreatorQuizzesView
from .infrastructure.views.get_quiz_scores_view import GetQuizScoresView
from .infrastructure.views.get_quiz_view import GetQuizView
from .infrastructure.views.get_user_quiz_progress_view import GetUserQuizProgressView
from .infrastructure.views.quizzes_dispatcher_view import QuizzesDispatcherView
from .infrastructure.views.send_invitation_view import SendInvitationView
from .infrastructure.views.submit_quiz_answers_view import SubmitQuizAnswersView

urlpatterns = [
    path("creators/<uuid:creator_id>/quizzes/", GetCreatorQuizzesView.as_view(), name="get-creator-quizzes"),
    path("quizzes/", QuizzesDispatcherView.as_view(), name="quizzes"),
    path("quizzes/<uuid:quiz_id>/", GetQuizView.as_view(), name="get-quiz"),
    path("quizzes/<uuid:quiz_id>/scores/", GetQuizScoresView.as_view(), name="get-quiz-scores"),
    path(
        "quizzes/<uuid:quiz_id>/creator-progress/",
        GetCreatorQuizProgressView.as_view(),
        name="get-creator-quiz-progress",
    ),
    path("quizzes/<uuid:quiz_id>/progress/", GetUserQuizProgressView.as_view(), name="get-user-quiz-progress"),
    path("quizzes/<uuid:quiz_id>/invitations/", SendInvitationView.as_view(), name="send-invitation"),
    path("invitations/<uuid:invitation_id>/accept/", AcceptInvitationView.as_view(), name="accept-invitation"),
    path("quizzes/<uuid:quiz_id>/submit/", SubmitQuizAnswersView.as_view(), name="submit-quiz-answers"),
]
