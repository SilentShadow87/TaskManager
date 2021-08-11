from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import ProfileModel
from .utils import send_confirmation_email, send_password_reset_email, send_link_to_mail
from .tokens import account_activation_token


# get default user model
UserModel = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user profile model."""
    class Meta:
        model = ProfileModel
        fields = ['is_verified', 'is_premium_member']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model."""
    profile = ProfileSerializer(read_only=True)
    email = serializers.EmailField(required=True,
                validators=[UniqueValidator(
                    queryset=UserModel.objects.all(),
                    message='Email address already in use.')
                    ]
                )

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password', 'profile']
        extra_kwargs = {
                'password': {'write_only': True}
                }


    def create(self, validated_data):
        """Create new user and send activation link to the user email."""
        password = validated_data.pop('password')
        user = UserModel(**validated_data)
        user.is_active = False # user must activate account

        user.set_password(password)
        user.save()

        ProfileModel.objects.create(user=user)

        # send activatiom email to the user
        # TODO: check async
        send_one_time_token(
                self.context['request'],
                user,
                account_activation_token.make_token(user),
                'account/activation_email.html',
                'Email confirmation'
                )

        return user

    def validate_password(self, value):
        """Validate password """
        password_validation.validate_password(value)
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer that is responsibile for setting new password."""
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def validate_old_password(self, value):
        """Check current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({'old_password': _('Wrong password.')})
        return value

    def validate(self, data):
        """Make sure that value from 'new_password1' and 'new_password2' match."""
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password2': _("The two password fields didn't match.")
                })
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def update(self, instance, validated_data):
        """Set new password."""
        instance.set_password(validated_data['new_password1'])
        instance.save()

        return instance


class ResetPasswordEmailSerializer(serializers.Serializer):
    """Serializer used for sending an email with instructions for a password reset."""
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate_email(self, value):
        """Check if user with specified email exists."""
        if not UserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError({'email': _('Email address does not exists.')})

        return value

    def save(self):
        """Send reset password link to the user mail."""
        email = self.validated_data['email']
        user = UserModel.objects.get(email=email)

        # send email
        send_one_time_token(
                self.context['request'],
                user,
                PasswordResetTokenGenerator().make_token(user)
                'account/password_reset_email.html',
                'Password reset',
                )
