import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from marketplace.models import Category, Product


@pytest.mark.django_db
def test_register_and_login():
    client = APIClient()
    res = client.post('/api/auth/register', {
        'username': 'u1', 'email': 'u1@test.com', 'password': 'abc12345', 'role': 'CLIENTE'
    }, format='json')
    assert res.status_code == 201

    res = client.post('/api/auth/login', {'username': 'u1', 'password': 'abc12345'}, format='json')
    assert res.status_code == 200
    assert 'access' in res.data


@pytest.mark.django_db
def test_products_public_filter_city():
    User = get_user_model()
    seller = User.objects.create_user(username='sell', password='x', role='VENDEDOR')
    cat = Category.objects.create(name='Ropa')
    Product.objects.create(seller=seller, name='Polera', description='x', price_bob=20, stock=5, category=cat, city='La Paz', published=True)
    Product.objects.create(seller=seller, name='Pantalon', description='x', price_bob=30, stock=5, category=cat, city='Santa Cruz', published=True)

    client = APIClient()
    res = client.get('/api/products/public?city=La Paz')
    assert res.status_code == 200
    assert len(res.data) == 1
