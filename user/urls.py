from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

urlpatterns = [
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("profile/", views.user_profile_view, name="user_profile"),
]
