from rest_framework import serializers
from django.contrib.auth import get_user_model


# get default user model
UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['username', 'email', 'password']
        extra_kwargs = {
                'password': {'write_only': True}
                }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel.(**validated_data)

        user.set_password(password)
        user.save()

        return user