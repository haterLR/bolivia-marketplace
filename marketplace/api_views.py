from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from chatapp.models import ChatThread
from users.permissions import IsAdminRole, IsSellerRole

from .models import Cart, CartItem, Order, Payment, Product, checkout_cart
from .payments import TigoMoneyProvider
from .permissions import IsSellerOwnerOrReadOnly
from .serializers import CartSerializer, OrderSerializer, PaymentSerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOwnerOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'seller').all()
        if self.action == 'public':
            qs = qs.filter(published=True)
            city = self.request.query_params.get('city')
            category = self.request.query_params.get('category')
            min_price = self.request.query_params.get('min_price')
            max_price = self.request.query_params.get('max_price')
            if city:
                qs = qs.filter(city__iexact=city)
            if category:
                qs = qs.filter(category_id=category)
            if min_price:
                qs = qs.filter(price_bob__gte=min_price)
            if max_price:
                qs = qs.filter(price_bob__lte=max_price)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'VENDEDOR':
            raise permissions.PermissionDenied('Solo vendedores')
        serializer.save(seller=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='public')
    def public(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(buyer=request.user)
        data = CartSerializer(cart).data
        data['total_bob'] = cart.total_bob()
        return Response(data)


class CartAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(buyer=request.user)
        product_id = request.data['product_id']
        quantity = int(request.data.get('quantity', 1))
        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
        if item.quantity > item.product.stock:
            return Response({'detail': 'Stock insuficiente'}, status=400)
        item.save()
        return Response(CartSerializer(cart).data)


class CartUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item = get_object_or_404(CartItem, id=request.data['item_id'], cart__buyer=request.user)
        qty = int(request.data['quantity'])
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            if qty > item.product.stock:
                return Response({'detail': 'Stock insuficiente'}, status=400)
            item.save()
        return Response({'detail': 'ok'})


class CartRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item = get_object_or_404(CartItem, id=request.data['item_id'], cart__buyer=request.user)
        item.delete()
        return Response({'detail': 'removed'})


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            orders = checkout_cart(
                buyer=request.user,
                address=request.data['address'],
                city=request.data['city'],
                notes=request.data.get('notes', ''),
            )
        except ValidationError as exc:
            return Response({'detail': str(exc)}, status=400)
        for order in orders:
            ChatThread.objects.get_or_create(order=order, buyer=order.buyer, seller=order.seller)
        return Response(OrderSerializer(orders, many=True).data)


class PaymentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order = get_object_or_404(Order, id=request.data['order_id'], buyer=request.user)
        payment = Payment.objects.create(
            order=order,
            method=request.data['method'],
            reference=request.data.get('reference', ''),
            metadata=request.data.get('metadata', {}),
        )
        if payment.method == Payment.Method.TIGO_MONEY:
            provider = TigoMoneyProvider()
            integration = provider.create_payment(order, callback_url=request.build_absolute_uri('/api/payments/webhook/tigomoney'))
            payment.reference = integration['reference']
            payment.metadata = integration
            payment.save(update_fields=['reference', 'metadata'])
        return Response(PaymentSerializer(payment).data)


class PaymentUploadProofView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payment = get_object_or_404(Payment, id=request.data['payment_id'], order__buyer=request.user)
        payment.proof_image = request.FILES.get('proof_image')
        payment.status = Payment.Status.VERIFYING
        payment.order.status = Order.Status.VERIFYING
        payment.order.save(update_fields=['status'])
        payment.save()
        return Response(PaymentSerializer(payment).data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def tigo_money_webhook(request):
    provider = TigoMoneyProvider()
    signature = request.headers.get('X-TM-Signature', '')
    payload = request.data
    if not provider.verify_callback(payload, signature):
        return Response({'detail': 'Firma inválida'}, status=400)
    payment = get_object_or_404(Payment, reference=payload.get('reference'))
    payment.status = Payment.Status.PAID
    payment.order.status = Order.Status.PAID
    payment.order.save(update_fields=['status'])
    payment.save(update_fields=['status'])
    return Response({'detail': 'ok'})


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.prefetch_related('items').all()
        if self.request.user.role == 'VENDEDOR':
            return qs.filter(seller=self.request.user)
        if self.request.user.role == 'ADMIN':
            return qs
        return qs.filter(buyer=self.request.user)


class PaymentMarkPaidView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payment = get_object_or_404(Payment, id=request.data['payment_id'])
        is_seller = request.user == payment.order.seller
        is_admin = request.user.role == 'ADMIN'
        if not (is_seller or is_admin):
            return Response({'detail': 'Sin permiso'}, status=403)
        payment.status = Payment.Status.PAID
        payment.order.status = Order.Status.PAID
        payment.order.save(update_fields=['status'])
        payment.save(update_fields=['status'])
        return Response(PaymentSerializer(payment).data)
