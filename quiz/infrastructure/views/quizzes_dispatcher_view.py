from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .create_quiz_view import CreateQuizView
from .get_user_quizzes_view import GetUserQuizzesView


class QuizzesDispatcherView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__get_view = GetUserQuizzesView()
        self.__post_view = CreateQuizView()

    def get(self, request: Request) -> Response:
        return self.__get_view.get(request)

    def post(self, request: Request) -> Response:
        return self.__post_view.post(request)
