from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .serializers import UserSerializer, ProfileSerializer, ChangePasswordSerializer, ResetPasswordEmailSerializer
from .authentication import ActivationTokenAuthentication, ResetPasswordTokenAuthentication


# get default user model
UserModel = get_user_model()

class UserListView(ListAPIView):
    """Retrieve user list. Only admins have permission to list users."""
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class UserCreateView(CreateAPIView):
    """Register new user."""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class ActivateAccount(APIView):
    """Activate user account. User is determined based on activation token."""
    authentication_classes = [ActivationTokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = request.user
        user.is_active = True
        user.profile.is_verified = True
        user.profile.save()

        return Response('Account id verified.')


class ChangePasswordView(UpdateAPIView):
    """Handle user attempt to change password."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user


class ResetPasswordView(APIView):
    """Handle forgotten password. Send a link with a password reset token to the supplied email address."""
    permission_classes = [AllowAny]

    def post(self ,request):
        serializer = ResetPasswordEmailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

        return Response('We have emailed you instructions for setting your password. If you do not receive an email, '
                        'please make sure you have entered the address you registered with.')


class PasswordResetCheckTokenView(APIView):
    """Check token used for reset user password."""
    authentication_classes = [ResetPasswordTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, uidb64, token):
        return Response({'uidb64': uidb64, 'token': token})


class PasswordResetConfirmView(APIView):
    """Handle user attempt to reset password."""
    authentication_classes = [ResetPasswordTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data, fields=('new_password1', 'new_password2'), context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True})

        return Response(serializer.errors)
