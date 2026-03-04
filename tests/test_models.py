import pytest
from django.contrib.auth import get_user_model

from marketplace.models import Cart, Category, Product, checkout_cart


@pytest.mark.django_db
def test_checkout_split_orders_by_seller():
    User = get_user_model()
    buyer = User.objects.create_user(username='buyer', password='x', role='CLIENTE')
    seller1 = User.objects.create_user(username='s1', password='x', role='VENDEDOR')
    seller2 = User.objects.create_user(username='s2', password='x', role='VENDEDOR')
    cat = Category.objects.create(name='Electrónica')
    p1 = Product.objects.create(seller=seller1, name='A', description='d', price_bob=10, stock=10, category=cat, city='La Paz', published=True)
    p2 = Product.objects.create(seller=seller2, name='B', description='d', price_bob=20, stock=10, category=cat, city='Cochabamba', published=True)
    cart = Cart.objects.create(buyer=buyer)
    cart.items.create(product=p1, quantity=2)
    cart.items.create(product=p2, quantity=1)

    orders = checkout_cart(buyer=buyer, address='Dir', city='La Paz')

    assert len(orders) == 2
    assert p1.__class__.objects.get(pk=p1.pk).stock == 8

