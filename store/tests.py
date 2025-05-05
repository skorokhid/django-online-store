# store/tests.py
import json
import pytest
from django.urls import reverse
from django.test import Client
from .models import Product, Order, OrderItem, Category

# Фікстури для спільного використання в тестах
@pytest.fixture
def test_category():
    return Category.objects.create(name="Test Category", slug="test-category")

@pytest.fixture
def test_product(test_category):
    return Product.objects.create(
        name="Test Product",
        description="Test Description",
        price=100.00,
        category=test_category,
        gender='U',
        size='M',
        color='Black',
        stock=10
        
    )

@pytest.mark.django_db
def test_product_list_view(client):
    response = client.get(reverse('product_list'))
    assert response.status_code == 200
    assert 'index.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_product_detail_view(client, test_category):
    product = Product.objects.create(
        name="Test Product",
        description="Test Description",
        price=100.00,
        category=test_category,
        gender='U',
        size='L',
        color='White',
        stock=5
    )
    response = client.get(reverse('product_detail', args=[product.pk]))
    assert response.status_code == 200
    assert 'product_page.html' in [t.name for t in response.templates]
    assert response.context['product'] == product

@pytest.mark.django_db
def test_add_to_cart_sets_cookie(client, test_category):
    product = Product.objects.create(
        name="Cart Product",
        description="Cart Description",
        price=50.00,
        category=test_category,
        gender='M',
        size='S',
        color='Red',
        stock=15
    )
    response = client.post(reverse('add_to_cart', args=[product.pk]), data={'quantity': 2})
    assert response.status_code == 302
    assert 'cart' in response.cookies

@pytest.mark.django_db
def test_view_cart_with_cookie(client, test_category):
    product = Product.objects.create(
        name="Cart Product",
        description="Cart Description",
        price=50.00,
        category=test_category,
        gender='F',
        size='M',
        color='Blue',
        stock=20
    )
    cart_data = json.dumps({str(product.pk): 2})
    client.cookies['cart'] = cart_data
    response = client.get(reverse('view_cart'))
    assert response.status_code == 200
    assert 'view_cart.html' in [t.name for t in response.templates]
    assert response.context['total'] == 100.00

@pytest.mark.django_db
def test_remove_from_cart(client, test_category):
    product = Product.objects.create(
        name="To Remove",
        description="Remove Description",
        price=30.00,
        category=test_category,
        gender='U',
        size='XL',
        color='Green',
        stock=8
    )
    client.cookies['cart'] = json.dumps({str(product.pk): 1})
    response = client.get(reverse('cart_remove', args=[product.pk]))
    assert response.status_code == 302
    new_cart = json.loads(response.cookies['cart'].value)
    assert str(product.pk) not in new_cart

@pytest.mark.django_db
def test_update_cart_quantity(client, test_category):
    product = Product.objects.create(
        name="Updater",
        description="Updater Description",
        price=10.00,
        category=test_category,
        gender='M',
        size='XS',
        color='Yellow',
        stock=12
    )
    client.cookies['cart'] = json.dumps({str(product.pk): 1})
    response = client.post(reverse('update_cart_quantity', args=[product.pk]), data={'quantity': 3})
    assert response.status_code == 302
    updated_cart = json.loads(response.cookies['cart'].value)
    assert updated_cart[str(product.pk)] == 3

@pytest.mark.django_db
def test_checkout_creates_order(client, test_category):
    product = Product.objects.create(
        name="CheckoutProduct",
        description="Checkout Description",
        price=20.00,
        category=test_category,
        gender='F',
        size='M',
        color='Pink',
        stock=6
    )
    client.cookies['cart'] = json.dumps({str(product.pk): 2})

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '12345678',
        'address': 'Some Street',
        'city': 'Some City',
        'postal_code': '12345'
    }

    response = client.post(reverse('checkout'), data=data)
    assert response.status_code == 302
    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1
    client.cookies.pop('cart', None)
    assert 'cart' not in client.cookies
@pytest.mark.django_db
def test_find_orders_found(client):
    order = Order.objects.create(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="111222333",
        address="Street 1",
        city="CityX",
        postal_code="00000",
        total=100.00,
        paid=False,
    )
    response = client.post(reverse('find_orders'), data={
        'first_name': 'Ali',
        'last_name': 'Smi',
        'contact': 'alice@example.com',
    })
    assert response.status_code == 200
    assert response.context['orders'].count() == 1

@pytest.mark.django_db
def test_find_orders_not_found(client):
    response = client.post(reverse('find_orders'), data={
        'first_name': 'Non',
        'last_name': 'Exist',
        'contact': 'noone@example.com',
    })
    assert response.status_code == 200
    assert response.context['orders'] is None