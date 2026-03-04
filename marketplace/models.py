from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Sum


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_bob = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=120)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.price_bob <= Decimal('0'):
            raise ValidationError('Precio debe ser mayor a 0 BOB')

    def __str__(self):
        return f'{self.name} - Bs {self.price_bob}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='products/')


class Cart(models.Model):
    buyer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)

    def total_bob(self):
        result = self.items.aggregate(total=Sum(F('quantity') * F('product__price_bob')))
        return result['total'] or Decimal('0')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError('Stock insuficiente')


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = 'creado', 'Creado'
        PAID = 'pagado', 'Pagado'
        VERIFYING = 'verificando', 'Verificando'
        SENT = 'enviado', 'Enviado'
        DELIVERED = 'entregado', 'Entregado'
        CANCELED = 'cancelado', 'Cancelado'

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sales_orders')
    total_bob = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price_bob = models.DecimalField(max_digits=12, decimal_places=2)


class Payment(models.Model):
    class Method(models.TextChoices):
        TIGO_MONEY = 'TIGO_MONEY', 'Tigo Money'
        QR_INTEROP = 'QR_INTEROP', 'QR Interop'
        TRANSFER = 'TRANSFERENCIA', 'Transferencia'

    class Status(models.TextChoices):
        CREATED = 'creado', 'Creado'
        VERIFYING = 'verificando', 'Verificando'
        PAID = 'pagado', 'Pagado'
        REJECTED = 'rechazado', 'Rechazado'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    reference = models.CharField(max_length=120, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    proof_image = models.ImageField(upload_to='payments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


def checkout_cart(*, buyer, address, city, notes=''):
    cart, _ = Cart.objects.get_or_create(buyer=buyer)
    items = list(cart.items.select_related('product').all())
    if not items:
        raise ValidationError('Carrito vacío')

    grouped = {}
    with transaction.atomic():
        for item in items:
            if item.quantity > item.product.stock:
                raise ValidationError(f'Stock insuficiente para {item.product.name}')
            grouped.setdefault(item.product.seller_id, []).append(item)

        orders = []
        for seller_id, seller_items in grouped.items():
            total = sum(i.quantity * i.product.price_bob for i in seller_items)
            order = Order.objects.create(
                buyer=buyer,
                seller_id=seller_id,
                total_bob=total,
                address=address,
                city=city,
                notes=notes,
            )
            for ci in seller_items:
                OrderItem.objects.create(
                    order=order,
                    product=ci.product,
                    quantity=ci.quantity,
                    unit_price_bob=ci.product.price_bob,
                )
                Product.objects.filter(id=ci.product_id).update(stock=F('stock') - ci.quantity)
            orders.append(order)
        cart.items.all().delete()
    return orders
