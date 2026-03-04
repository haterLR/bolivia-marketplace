from django.urls import path

from .web_views import (
    cart_view,
    checkout_page,
    home,
    order_chat,
    product_detail,
    seller_orders,
    seller_products,
)

urlpatterns = [
    path('', home, name='home'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_page, name='checkout'),
    path('seller/products/', seller_products, name='seller-products'),
    path('seller/orders/', seller_orders, name='seller-orders'),
    path('chat/order/<int:order_id>/', order_chat, name='order-chat'),
]
