from django.urls import path

from .infrastructure.views.accept_invitation_view import AcceptInvitationView
# from rest_framework_nested import routers
from .infrastructure.views.get_creator_quizzes_view import GetCreatorQuizzesView
from .infrastructure.views.get_quiz_scores_view import GetQuizScoresView
from .infrastructure.views.get_quiz_view import GetQuizView
from .infrastructure.views.quizzes_dispatcher_view import QuizzesDispatcherView
from .infrastructure.views.send_invitation_view import SendInvitationView
from .infrastructure.views.submit_quiz_answers_view import SubmitQuizAnswersView

urlpatterns = [
    path("1.0/creators/<uuid:creator_id>/quizzes/", GetCreatorQuizzesView.as_view(), name="get-creator-quizzes"),
    path("1.0/quizzes/", QuizzesDispatcherView.as_view(), name="quizzes"),
    path("1.0/quizzes/<uuid:quiz_id>/", GetQuizView.as_view(), name="get-quiz"),
    path("1.0/quizzes/<uuid:quiz_id>/scores/", GetQuizScoresView.as_view(), name="get-quiz-scores"),
    path("1.0/quizzes/<uuid:quiz_id>/invitations/", SendInvitationView.as_view(), name="send-invitation"),
    path("1.0/invitations/<uuid:invitation_id>/accept/", AcceptInvitationView.as_view(), name="accept-invitation"),
    path("1.0/quizzes/<uuid:quiz_id>/submit/", SubmitQuizAnswersView.as_view(), name="submit-quiz-answers"),

    # path('api/1.0/', include(router.urls)),
    # path('api/', include(quiz_router.urls)),
]
