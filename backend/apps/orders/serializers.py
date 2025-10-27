from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    price = serializers.DecimalField(source='book.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ("id", "book", "book_title", "price", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "user", "created_at", "items")
        read_only_fields = ("user",)


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "book", "book_title", "price", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "user", "status", "status_display", "total_amount", 
            "shipping_address", "shipping_city", "shipping_postal_code", 
            "notes", "created_at", "updated_at", "items"
        )
        read_only_fields = ("user", "status", "total_amount", "created_at", "updated_at")




