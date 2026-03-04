from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SELLER = 'VENDEDOR', 'Vendedor'
        CUSTOMER = 'CLIENTE', 'Cliente'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CUSTOMER)
    city = models.CharField(max_length=120, blank=True)


class SellerProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pendiente', 'Pendiente'
        APPROVED = 'aprobado', 'Aprobado'
        REJECTED = 'rechazado', 'Rechazado'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=200)
    nit = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.business_name} ({self.status})'
