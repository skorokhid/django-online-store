# store/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import Product, Category, Order, OrderItem
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            current_price=90.00,
            category=self.category,
            description="Test description",
            available=True
        )
    
    def test_category_creation(self):
        self.assertEqual(str(self.category), "Test Category")
    
    def test_product_creation(self):
        self.assertEqual(str(self.product), "Test Product")
        self.assertEqual(self.product.current_price, 90.00)
        self.assertTrue(self.product.available)

class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test Category")
        cls.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            current_price=90.00,
            category=cls.category,
            description="Test description",
            available=True
        )
    
    def test_product_list_view(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")
        self.assertTemplateUsed(response, 'index.html')
    
    def test_product_detail_view(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")
        self.assertTemplateUsed(response, 'product_page.html')

class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test Category")
        cls.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            current_price=90.00,
            category=cls.category,
            description="Test description",
            available=True
        )
    
    def test_add_to_cart(self):
        response = self.client.post(
            reverse('store:add_to_cart', args=[self.product.pk]),
            {'quantity': 2},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart', response.cookies)
        
        cart = json.loads(response.cookies['cart'].value)
        self.assertEqual(cart[str(self.product.pk)], 2)
    
    def test_view_cart(self):
        # Спочатку додаємо товар до кошика
        self.client.post(
            reverse('store:add_to_cart', args=[self.product.pk]),
            {'quantity': 1}
        )
        
        response = self.client.get(reverse('store:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")
        self.assertTemplateUsed(response, 'view_cart.html')

class OrderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test Category")
        cls.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            current_price=90.00,
            category=cls.category,
            description="Test description",
            available=True
        )
    
    def test_checkout_process(self):
        # Додаємо товар до кошика
        self.client.post(
            reverse('store:add_to_cart', args=[self.product.pk]),
            {'quantity': 1}
        )
        
        # Відправляємо форму оформлення замовлення
        response = self.client.post(
            reverse('store:checkout'),
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'phone': '123456789',
                'address': 'Test Address',
                'city': 'Test City',
                'postal_code': '12345'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.total, 90.00)
        self.assertEqual(order.first_name, 'John')
        
        # Перевіряємо, що кошик очистився
        self.assertNotIn('cart', response.cookies)