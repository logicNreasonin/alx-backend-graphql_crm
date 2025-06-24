import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField # Task 3: Import for filtering
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter # Task 3: Import your filter classes
import re
from django.db import transaction #, IntegrityError # IntegrityError not directly used in this snippet
from django.utils import timezone
from decimal import Decimal

from crm import models

# Unused import 'from crm import models' removed as models are already imported from .models

# --- Graphene Object Types (representing Django models) ---
# Task 3: Changed to XxxNode and implementing graphene.relay.Node for DjangoFilterConnectionField
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at", "orders")
        filterset_class = CustomerFilter # Task 3: Link filter class
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at", "orders")
        filterset_class = ProductFilter # Task 3: Link filter class
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount", "created_at")
        filterset_class = OrderFilter # Task 3: Link filter class
        interfaces = (graphene.relay.Node,)

    # Explicit resolvers can still be used if needed for custom logic,
    # but ensure they return instances compatible with the Node structure.
    # For basic field resolution, DjangoObjectType handles it.
    # If resolving related fields like 'customer' or 'products' when they are also Nodes:
    customer = graphene.Field(lambda: CustomerNode) # Use lambda to avoid circular import issues if defined later
    products = graphene.List(lambda: ProductNode)

    def resolve_products(self, info):
        return self.products.all() # Graphene handles resolving these to ProductNode

    def resolve_customer(self, info):
        return self.customer # Graphene handles resolving this to CustomerNode

    # Required for Node interface if you want to customize how nodes are fetched by global ID
    @classmethod
    def get_node(cls, info, id):
        try:
            return cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            return None

# --- Input Object Types for Mutations (from your provided code) ---
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.Date()

# --- Helper for Phone Validation (from your provided code) ---
def is_valid_phone(phone_number):
    phone_pattern = re.compile(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$")
    return bool(phone_pattern.match(phone_number))

# --- Mutation Classes (from your provided code) ---
# Task 3 Note: Ensure the output fields of mutations (e.g., customer, product, order)
# use the Node types (CustomerNode, ProductNode, OrderNode) if you want full consistency
# with the query side. For now, I'm keeping them as XxxType (which will resolve to XxxNode
# if XxxType is an alias for XxxNode or if Graphene can map them based on the model).
# For clarity, it's better to update them explicitly.
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerNode) # Updated to CustomerNode
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        validation_errors = []
        if input.phone and not is_valid_phone(input.phone):
            validation_errors.append(f"Invalid phone number format: {input.phone}.")
        if Customer.objects.filter(email=input.email).exists():
            validation_errors.append(f"Email already exists: {input.email}.")
        if validation_errors:
            return CreateCustomer(customer=None, message="Customer creation failed.", errors=validation_errors)
        try:
            customer_instance = Customer.objects.create(name=input.name, email=input.email, phone=input.phone)
            return CreateCustomer(customer=customer_instance, message="Customer created successfully.", errors=None)
        except Exception as e:
            return CreateCustomer(customer=None, message="Customer creation failed.", errors=[str(e)])

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerNode) # Updated to CustomerNode
    errors = graphene.List(graphene.String)

    def mutate(self, info, input_list):
        created_customers_list = []
        error_messages = []
        for customer_data in input_list:
            current_customer_errors = []
            if customer_data.phone and not is_valid_phone(customer_data.phone):
                current_customer_errors.append(f"Cust '{customer_data.name}': Invalid phone.")
            if Customer.objects.filter(email=customer_data.email).exists():
                current_customer_errors.append(f"Cust '{customer_data.name}': Email exists.")
            if current_customer_errors:
                error_messages.extend(current_customer_errors)
                continue
            try:
                customer_instance = Customer.objects.create(
                    name=customer_data.name, email=customer_data.email, phone=customer_data.get('phone'))
                created_customers_list.append(customer_instance)
            except Exception as e:
                error_messages.append(f"Cust '{customer_data.name}': Failed. Error: {str(e)}")
        return BulkCreateCustomers(customers=created_customers_list, errors=error_messages if error_messages else None)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductNode) # Updated to ProductNode
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        validation_errors = []
        if input.price <= Decimal('0'):
            validation_errors.append("Price must be positive.")
        if input.stock < 0:
            validation_errors.append("Stock cannot be negative.")
        if validation_errors:
            return CreateProduct(product=None, errors=validation_errors)
        try:
            product_instance = Product.objects.create(name=input.name, price=input.price, stock=input.stock)
            return CreateProduct(product=product_instance, errors=None)
        except Exception as e:
            return CreateProduct(product=None, errors=[f"Product creation failed: {str(e)}"])

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderNode) # Updated to OrderNode
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        validation_errors = []
        customer_id_str = input.customer_id
        product_ids_str_list = input.product_ids
        order_date_val = input.get('order_date', timezone.now().date())

        try:
            customer_instance = Customer.objects.get(pk=int(customer_id_str))
        except Customer.DoesNotExist:
            return CreateOrder(order=None, errors=[f"Customer ID '{customer_id_str}' not found."])
        except ValueError:
             return CreateOrder(order=None, errors=[f"Invalid Customer ID format: '{customer_id_str}'."])

        if not product_ids_str_list:
            validation_errors.append("At least one product ID must be provided.")
        
        linked_products = []
        calculated_total_amount = Decimal('0.00')

        for p_id_str in product_ids_str_list:
            try:
                product_instance = Product.objects.get(pk=int(p_id_str))
                if product_instance.stock <= 0:
                     validation_errors.append(f"Product '{product_instance.name}' (ID: {p_id_str}) is out of stock.")
                else:
                    linked_products.append(product_instance)
                    calculated_total_amount += product_instance.price
            except Product.DoesNotExist:
                validation_errors.append(f"Product ID '{p_id_str}' not found.")
            except ValueError:
                 validation_errors.append(f"Invalid Product ID format: '{p_id_str}'.")
        
        if not linked_products and not validation_errors and product_ids_str_list:
             validation_errors.append("No valid products could be added to the order.")

        if validation_errors:
            return CreateOrder(order=None, errors=validation_errors)

        try:
            order_instance = Order.objects.create(
                customer=customer_instance, order_date=order_date_val, total_amount=calculated_total_amount)
            order_instance.products.set(linked_products)
            
            for p in linked_products:
                Product.objects.filter(pk=p.pk).update(stock=models.F('stock') - 1)

            return CreateOrder(order=order_instance, errors=None)
        except Exception as e:
            return CreateOrder(order=None, errors=[f"Failed to create order: {str(e)}"])


# --- Query Class (Updated for Task 3) ---
class Query(graphene.ObjectType):
    # Relay-style node field for fetching any object by its global ID
    node = graphene.relay.Node.Field() # Task 3: Standard Relay node field

    # Using DjangoFilterConnectionField for list queries with filtering and pagination
    all_customers = DjangoFilterConnectionField(CustomerNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    # The explicit resolve_all_xxx and xxx_by_id methods are no longer needed
    # for these list fields when using DjangoFilterConnectionField.
    # The generic 'node' field can be used for fetching by ID, or you can
    # add specific Node.Field(YourNodeType) if desired for individual lookups,
    # but 'node = graphene.relay.Node.Field()' is generally sufficient.

# --- Mutation Class (from your provided code, with updated return types) ---
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()