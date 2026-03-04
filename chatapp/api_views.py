from rest_framework import generics, permissions

from .models import ChatMessage, ChatThread
from .serializers import ChatMessageSerializer, ChatThreadSerializer


class ThreadListView(generics.ListAPIView):
    serializer_class = ChatThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatThread.objects.filter(buyer=user) | ChatThread.objects.filter(seller=user)


class MessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        user = self.request.user
        return ChatMessage.objects.filter(thread_id=thread_id, thread__buyer=user) | ChatMessage.objects.filter(thread_id=thread_id, thread__seller=user)
