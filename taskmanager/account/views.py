from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .serializers import UserSerializer, ProfileSerializer
from .tokens import account_activation_token


# get default user model
UserModel = get_user_model()

class UserListView(ListAPIView):
    """Retrieve user list."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class UserCreateView(CreateAPIView):
    """Reister new user."""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class ActivateAccount(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        user = None
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid) 

        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            pass

        if user is not None and account_activation_token.check_token(user,
                token):
            user.profile.is_verified = True
            user.profile.save()

            return Response('Account id verified.')

        return Response('The confirmation link was invalid, possibly because it has already been used.')
