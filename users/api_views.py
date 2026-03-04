from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, throttling
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import SellerProfile
from .permissions import IsAdminRole
from .serializers import RegisterSerializer, SellerApplySerializer, SellerProfileSerializer

User = get_user_model()


class LoginThrottle(throttling.UserRateThrottle):
    scope = 'login'


class LoginView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]


class RefreshView(TokenRefreshView):
    pass


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class SellerApplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'VENDEDOR':
            return Response({'detail': 'Solo rol vendedor puede aplicar.'}, status=400)
        profile, created = SellerProfile.objects.get_or_create(user=request.user)
        serializer = SellerApplySerializer(profile, data=request.data, partial=not created)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SellerProfileSerializer(profile).data)


class SellerMeView(generics.RetrieveAPIView):
    serializer_class = SellerProfileSerializer

    def get_object(self):
        return self.request.user.seller_profile


class SellerDetailView(generics.RetrieveAPIView):
    queryset = SellerProfile.objects.select_related('user')
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.AllowAny]


class AdminApproveSellerView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def post(self, request):
        seller_id = request.data.get('seller_id')
        status_value = request.data.get('status', SellerProfile.Status.APPROVED)
        profile = generics.get_object_or_404(SellerProfile, id=seller_id)
        if status_value not in SellerProfile.Status.values:
            return Response({'detail': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
        profile.status = status_value
        profile.save(update_fields=['status'])
        return Response(SellerProfileSerializer(profile).data)
