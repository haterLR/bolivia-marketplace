from rest_framework import serializers

from .models import ChatMessage, ChatThread


class ChatThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatThread
        fields = ('id', 'order', 'buyer', 'seller')


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'thread', 'sender', 'text', 'attachment', 'created_at')
