from decimal import Decimal
from django.conf import settings
from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, quantity=1, size=None, color=None):
        product_id = str(product_id)
        key = f"{product_id}:{size}:{color}"

        if key not in self.cart:
            self.cart[key] = {
                'product_id': product_id,
                'quantity': 0,
                'size': size,
                'color': color,
            }
        self.cart[key]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def __iter__(self):
        for key, item in self.cart.items():
            product = Product.objects.get(id=item['product_id'])
            yield {
                'key': key,
                'product': product,
                'quantity': item['quantity'],
                'size': item['size'],
                'color': item['color'],
                'price': product.current_price,
                'total_price': product.current_price * item['quantity'],
            }

    def get_total_price(self):
        return sum(item['total_price'] for item in self)

    def clear(self):
        self.session['cart'] = {}
        self.save()
