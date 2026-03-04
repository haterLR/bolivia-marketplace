from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    CartAddView,
    CartRemoveView,
    CartUpdateView,
    CartView,
    CheckoutView,
    OrderListView,
    PaymentCreateView,
    PaymentMarkPaidView,
    PaymentUploadProofView,
    ProductViewSet,
    tigo_money_webhook,
)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('cart', CartView.as_view()),
    path('cart/add', CartAddView.as_view()),
    path('cart/remove', CartRemoveView.as_view()),
    path('cart/update', CartUpdateView.as_view()),
    path('checkout', CheckoutView.as_view()),
    path('orders', OrderListView.as_view()),
    path('payments/create', PaymentCreateView.as_view()),
    path('payments/upload-proof', PaymentUploadProofView.as_view()),
    path('payments/mark-paid', PaymentMarkPaidView.as_view()),
    path('payments/webhook/tigomoney', tigo_money_webhook),
]
