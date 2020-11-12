from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserSerializer

UserModel = get_user_model()

class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class UserCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()

