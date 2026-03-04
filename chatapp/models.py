from django.conf import settings
from django.db import models

from marketplace.models import Order


class ChatThread(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='chat_thread')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_threads')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_threads')


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    attachment = models.ImageField(upload_to='chat/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
