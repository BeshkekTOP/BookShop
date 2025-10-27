from django.urls import path
from .views import SalesStatsView, TopBooksView

urlpatterns = [
    path('analytics/sales/', SalesStatsView.as_view(), name='analytics-sales'),
    path('analytics/top-books/', TopBooksView.as_view(), name='analytics-top-books'),
]




