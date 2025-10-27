from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartView, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('cart/', CartView.as_view(), name='api-cart'),
] + router.urls





