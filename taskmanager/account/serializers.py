from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

from .models import ProfileModel
from .utils import send_confirmation_email


# get default user model
UserModel = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileModel
        fields = ['is_verified', 'is_premium_member']


class UserSerializer(serializers.ModelSerializer):
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
        password = validated_data.pop('password')
        user = UserModel(**validated_data)
        user.is_active = False
        user.set_password(password)
        user.save()

        ProfileModel.objects.create(user=user)

        send_confirmation_email(self.context['request'], user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({'old_password': _('Wrong password.')})

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password2': _("The two password fields didn't match.")
                })
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password1'])
        instance.save()

        return instance
