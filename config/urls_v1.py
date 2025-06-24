"""
API v1 URL Configuration
"""

from django.urls import path, include

# V1 API endpoints
urlpatterns = [
    path("", include("user.urls_v1")),
    path("", include("quiz.urls_v1")),
]
