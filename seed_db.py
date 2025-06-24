# alx_backend_graphql_crm/seed_db.py
import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from django.db import transaction
from crm.models import Customer, Product, Order

def seed_data():
    print("Seeding database...")
    with transaction.atomic():
        # Clear existing data (optional, be careful in production)
        Order.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        print("Existing data cleared.")

        # Create Customers
        c1 = Customer.objects.create(name="Alice Wonderland", email="alice@example.com", phone="+12223334444")
        c2 = Customer.objects.create(name="Bob The Builder", email="bob@example.com", phone="123-456-7890")
        c3 = Customer.objects.create(name="Charlie Chaplin", email="charlie@example.com")
        print(f"Created Customers: {c1.name}, {c2.name}, {c3.name}")

        # Create Products
        p1 = Product.objects.create(name="Laptop Pro", description="High-end laptop", price=Decimal("1200.50"), stock=10)
        p2 = Product.objects.create(name="Wireless Mouse", description="Ergonomic mouse", price=Decimal("25.99"), stock=50)
        p3 = Product.objects.create(name="Keyboard Classic", description="Mechanical keyboard", price=Decimal("75.00"), stock=30)
        p4 = Product.objects.create(name="Monitor UltraWide", description="34-inch ultrawide monitor", price=Decimal("450.75"), stock=5)
        print(f"Created Products: {p1.name}, {p2.name}, {p3.name}, {p4.name}")

        # Create Orders
        order1 = Order.objects.create(customer=c1, total_amount=p1.price + p2.price)
        order1.products.set([p1, p2])
        print(f"Created Order 1 for {c1.name} with products: {p1.name}, {p2.name}. Total: {order1.total_amount}")

        order2 = Order.objects.create(customer=c2, total_amount=p3.price)
        order2.products.set([p3])
        print(f"Created Order 2 for {c2.name} with product: {p3.name}. Total: {order2.total_amount}")
        
        order3 = Order.objects.create(customer=c1, total_amount=p4.price + p2.price) # Alice orders again
        order3.products.set([p4, p2])
        print(f"Created Order 3 for {c1.name} with products: {p4.name}, {p2.name}. Total: {order3.total_amount}")


    print("Database seeding completed.")

if __name__ == '__main__':
    seed_data()