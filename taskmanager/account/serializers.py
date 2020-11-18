from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

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
    email = serializers.EmailField(required=True
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
