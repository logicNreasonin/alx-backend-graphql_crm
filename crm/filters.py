# crm/filters.py
import django_filters
from django.db.models import Q # For complex lookups
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    # Field names here will be used to generate GraphQL filter arguments
    # e.g., 'name_Icontains' for name__icontains
    name = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    email = django_filters.CharFilter(lookup_expr='icontains', field_name='email')
    
    # For date range, Graphene-Django typically uses _after and _before with DateFromToRangeFilter
    # To match checkpoint's 'createdAtGte' and 'createdAtLte', we define them explicitly:
    created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    # Challenge: Custom filter for phone number pattern (e.g., starts with +1)
    phone_starts_with = django_filters.CharFilter(method='filter_phone_starts_with', label="Phone starts with")

    class Meta:
        model = Customer
        fields = { # These are fields that can be filtered with exact match by default if not specified above
            'name': ['exact', 'icontains'], # 'name' here refers to the GraphQL field 'name', not model field.
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'], # Allows created_At, created_At_Gte, created_At_Lte
        }
        # Note: Fields defined explicitly above (like 'name' with icontains) will override these.
        # The 'fields' dict primarily helps django-filter auto-generate filters if you don't define them.
        # For DjangoFilterConnectionField, it's often cleaner to define each filter explicitly as above for clarity in GraphQL.

    def filter_phone_starts_with(self, queryset, name, value):
        # name is 'phone_starts_with' (the filter field name)
        # value is the string provided (e.g., "+1")
        if value: # Only filter if a value is provided
            return queryset.filter(phone__startswith=value)
        return queryset

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', field_name='name')
    
    # To match checkpoint's 'priceGte' and 'priceLte'
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # To match checkpoint's 'stockGte' and 'stockLte' (if needed, checkpoint only showed orderBy)
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    stock_exact = django_filters.NumberFilter(field_name='stock', lookup_expr='exact') # For exact stock match

    # Challenge: Filter products with low stock (e.g., stock < 10)
    # We can expose this as a boolean filter in GraphQL
    is_low_stock = django_filters.BooleanFilter(method='filter_is_low_stock', label="Is low stock (less than 10)?")

    # For sorting (handled by DjangoFilterConnectionField and OrderingFilter)
    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('stock', 'stock'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = Product
        fields = ['name', 'price_gte', 'price_lte', 'stock_gte', 'stock_lte', 'stock_exact', 'is_low_stock']

    def filter_is_low_stock(self, queryset, name, value):
        # name is 'is_low_stock'
        # value is True or False
        if value is True:
            return queryset.filter(stock__lt=10)
        elif value is False: # Optionally filter for not low stock
             return queryset.filter(stock__gte=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    # To match checkpoint's 'totalAmountGte' and 'totalAmountLte'
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')

    # To match checkpoint's 'orderDateGte' and 'orderDateLte'
    order_date_gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')

    # Filter by customer's name (case-insensitive partial match)
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')

    # Filter by product's name (case-insensitive partial match)
    # This will filter orders that contain *any* product matching the name.
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains', distinct=True)

    # Challenge: Allow filtering orders that include a specific product ID.
    has_product_id = django_filters.NumberFilter(method='filter_has_product_id', label="Order includes Product ID")
    
    # For sorting
    order_by = django_filters.OrderingFilter(
        fields=(
            ('customer__name', 'customer_name'), # Sort by customer's name
            ('order_date', 'order_date'),
            ('total_amount', 'total_amount'),
            ('id', 'id'), # useful for consistent pagination
        )
    )

    class Meta:
        model = Order
        fields = [
            'total_amount_gte', 'total_amount_lte', 
            'order_date_gte', 'order_date_lte',
            'customer_name', 'product_name', 'has_product_id'
        ]

    def filter_has_product_id(self, queryset, name, value):
        # name is 'has_product_id'
        # value is the product ID
        if value is not None:
            return queryset.filter(products__id=value).distinct()
        return queryset