from django.urls import path

from .api_views import (
    AdminApproveSellerView,
    LoginView,
    RefreshView,
    RegisterView,
    SellerApplyView,
    SellerDetailView,
    SellerMeView,
)

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='auth-login'),
    path('auth/refresh', RefreshView.as_view(), name='auth-refresh'),
    path('auth/register', RegisterView.as_view(), name='auth-register'),
    path('sellers/apply', SellerApplyView.as_view(), name='seller-apply'),
    path('sellers/me', SellerMeView.as_view(), name='seller-me'),
    path('sellers/<int:pk>', SellerDetailView.as_view(), name='seller-detail'),
    path('admin/sellers/approve', AdminApproveSellerView.as_view(), name='admin-seller-approve'),
]
