# crm/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import re # For phone number validation
from decimal import Decimal

def validate_phone_number(value):
    # Example regex: allows +1234567890, 123-456-7890, (123)456-7890, 1234567890
    # You might want a stricter or more comprehensive regex depending on requirements
    phone_regex = re.compile(r"^\+?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")
    if not phone_regex.match(value) and value: # only validate if a value is provided
        raise ValidationError(
            "Phone number must be in a valid format (e.g., +1234567890, 123-456-7890)."
        )

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone_number])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.price <= 0:
            raise ValidationError("Price must be positive.")
        # Stock is PositiveIntegerField, so it's already non-negative by model definition

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_amount(self):
        # This method should be called before saving if products are set
        # Note: self.products.all() might not work correctly until the order and its M2M relations are saved.
        # It's better to calculate based on product instances passed during creation.
        # For simplicity in mutations, we will calculate it there.
        # If products are already associated (e.g. for an existing order):
        # total = sum(product.price for product in self.products.all())
        # self.total_amount = Decimal(total)
        # However, this line is problematic here as it can cause recursion on save or requires products to be already saved.
        # We will handle total_amount calculation explicitly in the mutation.
        pass


    def save(self, *args, **kwargs):
        # `calculate_total_amount` is better handled in the mutation or signal
        # to ensure products are correctly accounted for, especially for new orders.
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"