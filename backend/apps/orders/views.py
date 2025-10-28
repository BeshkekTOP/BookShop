from decimal import Decimal
from django.db import transaction
from rest_framework import permissions, status, views, viewsets, filters
from rest_framework.response import Response

from backend.apps.catalog.models import Inventory, Book
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_authenticated


class CartView(views.APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_id = serializer.validated_data["book"].id
        quantity = serializer.validated_data["quantity"]
        item, created = CartItem.objects.get_or_create(cart=cart, book_id=book_id, defaults={"quantity": quantity})
        if not created:
            item.quantity += quantity
            item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response(status=status.HTTP_204_NO_CONTENT)
        CartItem.objects.filter(cart=cart, book_id=request.data.get("book")).delete()
        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).order_by("-created_at")
        
        # Администраторы могут видеть все заказы
        if self.request.user.is_staff:
            queryset = Order.objects.all().order_by("-created_at")
            
        return queryset

    def get_permissions(self):
        # Для обновления и удаления нужны особые права
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user).prefetch_related("items__book").first()
        if not cart or cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Stock check
        for item in cart.items.all():
            inv = Inventory.objects.select_for_update().get(book=item.book)
            if inv.available < item.quantity:
                return Response({"detail": f"Not enough stock for {item.book.title}"}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = Order.objects.create(
            user=user, 
            status="processing", 
            total_amount=Decimal("0"),
            shipping_address=request.data.get('shipping_address', ''),
            shipping_city=request.data.get('shipping_city', ''),
            notes=request.data.get('notes', '')
        )
        total = Decimal("0")
        for item in cart.items.all():
            price = item.book.price
            OrderItem.objects.create(order=order, book=item.book, price=price, quantity=item.quantity)
            total += price * item.quantity
            inv = Inventory.objects.select_for_update().get(book=item.book)
            inv.stock = max(0, inv.stock - item.quantity)
            inv.save()
        order.total_amount = total
        order.save()

        # Clear cart
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
