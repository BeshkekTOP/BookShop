from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalesStatsView, TopBooksView, DashboardStatsView,
    PageViewViewSet, BookViewViewSet, SearchQueryViewSet, PurchaseEventViewSet
)

router = DefaultRouter()
router.register(r'page-views', PageViewViewSet)
router.register(r'book-views', BookViewViewSet)
router.register(r'search-queries', SearchQueryViewSet)
router.register(r'purchase-events', PurchaseEventViewSet)

urlpatterns = [
    path('analytics/sales/', SalesStatsView.as_view(), name='analytics-sales'),
    path('analytics/top-books/', TopBooksView.as_view(), name='analytics-top-books'),
    path('analytics/dashboard/', DashboardStatsView.as_view(), name='analytics-dashboard'),
    path('analytics/', include(router.urls)),
]




