from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from chatapp.models import ChatMessage, ChatThread

from .models import Cart, CartItem, Order, Product, checkout_cart


def home(request):
    qs = Product.objects.filter(published=True)
    q = request.GET.get('q')
    city = request.GET.get('city')
    category = request.GET.get('category')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if city:
        qs = qs.filter(city__iexact=city)
    if category:
        qs = qs.filter(category__name__iexact=category)
    return render(request, 'shop/home.html', {'products': qs[:50]})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, published=True)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=request.POST['product_id'])
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})
        if not created and item.quantity < product.stock:
            item.quantity += 1
            item.save()
        return redirect('cart')
    return render(request, 'shop/cart.html', {'cart': cart})


@login_required
def checkout_page(request):
    if request.method == 'POST':
        checkout_cart(
            buyer=request.user,
            address=request.POST['address'],
            city=request.POST['city'],
            notes=request.POST.get('notes', ''),
        )
        return redirect('seller-orders')
    return render(request, 'shop/checkout.html')


@login_required
def seller_products(request):
    products = Product.objects.filter(seller=request.user)
    return render(request, 'seller/products.html', {'products': products})


@login_required
def seller_orders(request):
    orders = Order.objects.filter(seller=request.user)
    return render(request, 'seller/orders.html', {'orders': orders})


@login_required
def order_chat(request, order_id):
    thread = get_object_or_404(ChatThread, order_id=order_id)
    messages = ChatMessage.objects.filter(thread=thread).select_related('sender').order_by('created_at')
    return render(request, 'chat/order_chat.html', {'thread': thread, 'messages': messages})
