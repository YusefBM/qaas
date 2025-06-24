from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, UserSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    try:
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=first_name, last_name=last_name
        )

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response(
            {
                "message": "User created successfully",
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(access_token),
            },
            status=status.HTTP_201_CREATED,
        )

    except IntegrityError:
        return Response({"error": "Username or email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Failed to create user"}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user data along with tokens"""

    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view"""

    serializer_class = CustomTokenRefreshSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    """Logout view that blacklists the refresh token"""
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_profile_view(request):
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    else:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
