from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserSerializer


# get default user model
UserModel = get_user_model()

class UserListView(ListAPIView):
    """Retrieve user list."""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class UserCreateView(CreateAPIView):
    """Reister new user."""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()

