from rest_framework import serializers

from .models import Cart, CartItem, Category, Order, OrderItem, Payment, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')


class ProductSerializer(serializers.ModelSerializer):
    photos = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'seller', 'name', 'description', 'price_bob', 'stock', 'category',
            'city', 'published', 'photos', 'created_at'
        )
        read_only_fields = ('seller',)


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'product_detail')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_bob = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'buyer', 'items', 'total_bob')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'unit_price_bob')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'buyer', 'seller', 'total_bob', 'status', 'address', 'city', 'notes', 'items', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('status',)
