from django.urls import path

from .api_views import MessageListView, ThreadListView

urlpatterns = [
    path('chat/threads', ThreadListView.as_view()),
    path('chat/threads/<int:thread_id>/messages', MessageListView.as_view()),
]
