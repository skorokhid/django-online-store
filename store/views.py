from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def product_list(request):
    products = Product.objects.all()  # Отримуємо всі продукти з бази даних
    return render(request, 'index.html', {'products': products})

def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    # Знайти інші товари тієї ж категорії, крім поточного товару
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)
    
    return render(request, 'product_page.html', {
        'product': product,
        'related_products': related_products,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.COOKIES.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = {}

    product_key = str(product_id)
    if product_key in cart:
        cart[product_key] += quantity
    else:
        cart[product_key] = quantity

    response = redirect('view_cart')
    response.set_cookie('cart', json.dumps(cart), max_age=7 * 24 * 60 * 60)  # 1 тиждень
    return response

def view_cart(request):
    cart = request.COOKIES.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = {}

    products = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        price = float(product.current_price)
        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': quantity * price,
        })
        total += quantity * price

    return render(request, 'view_cart.html', {'products': products, 'total': total})



def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart = request.COOKIES.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = {}

    product_key = str(product.pk)
    if product_key in cart:
        del cart[product_key]

    response = redirect('view_cart')
    response.set_cookie('cart', json.dumps(cart), max_age=7 * 24 * 60 * 60)
    return response


@require_POST
def update_cart_quantity(request, product_id):
    cart = request.COOKIES.get('cart')
    if cart:
        cart = json.loads(cart)
    else:
        cart = {}

    product_key = str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart[product_key] = quantity
    else:
        if product_key in cart:
            del cart[product_key]

    response = redirect('view_cart')
    response.set_cookie('cart', json.dumps(cart), max_age=7 * 24 * 60 * 60)
    return response




@require_POST
def checkout(request):
    cart = request.COOKIES.get('cart')
    if not cart:
        return redirect('view_cart')
    
    cart = json.loads(cart)

    if not cart:
        return redirect('view_cart')
    
    # Дані форми
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    city = request.POST.get('city')
    postal_code = request.POST.get('postal_code')
    
    total = 0
    items = []
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        price = product.current_price
        total += price * quantity
        items.append((product, price, quantity))
    
    # Створити замовлення
    order = Order.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        postal_code=postal_code,
        total=total,
        paid=False,
    )
    
    for product, price, quantity in items:
        OrderItem.objects.create(
            order=order,
            product=product,
            price=price,
            quantity=quantity,
        )
    
    response = redirect('product_list')
    response.delete_cookie('cart')  # Очистити кошик після замовлення
    return response

def find_orders(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        
        # Пошук замовлень за ім'ям, телефоном або email
        orders = Order.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name, email__icontains=contact) | \
                Order.objects.filter(phone__icontains=contact)
        
        if orders.exists():
            return render(request, 'find_orders.html', {'orders': orders})
        else:
            return render(request, 'find_orders.html', {'orders': None, 'message': 'Замовлення не знайдено.'})
    
    return render(request, 'find_orders.html')
