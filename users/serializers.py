from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SellerProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'city')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SellerApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ('business_name', 'nit', 'description')


class SellerProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = SellerProfile
        fields = ('id', 'user', 'business_name', 'nit', 'description', 'status', 'created_at')
