from datetime import datetime, timedelta
from django.db.models import Sum, F, Count, Avg
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, views, viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import csv

from backend.apps.orders.models import OrderItem
# from .models import PageView, BookView, SearchQuery, PurchaseEvent  # Временно отключено
# from .serializers import PageViewSerializer, BookViewSerializer, SearchQuerySerializer, PurchaseEventSerializer  # Временно отключено


class SalesStatsView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        export = request.query_params.get('export')
        start_dt = parse_datetime(start) if start else None
        end_dt = parse_datetime(end) if end else None
        qs = OrderItem.objects.select_related('order').all()
        if start_dt:
            qs = qs.filter(order__created_at__gte=start_dt)
        if end_dt:
            qs = qs.filter(order__created_at__lte=end_dt)

        if export == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="sales.csv"'
            writer = csv.writer(response)
            writer.writerow(["order_id", "book_id", "book_title", "price", "quantity", "created_at"])
            for item in qs.select_related('book', 'order').all():
                writer.writerow([item.order_id, item.book_id, item.book.title, item.price, item.quantity, item.order.created_at.isoformat()])
            return response

        total_revenue = qs.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        total_items = qs.aggregate(total=Sum('quantity'))['total'] or 0
        return Response({"total_revenue": total_revenue, "total_items": total_items})


class TopBooksView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        qs = (
            OrderItem.objects.values('book__id', 'book__title')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:limit]
        )
        return Response(list(qs))


# Временно отключено - требуется восстановление старых моделей
# class PageViewViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = PageView.objects.all()
#     serializer_class = PageViewSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['user', 'path']
#     search_fields = ['path', 'user_agent']
#     ordering_fields = ['timestamp']
#     ordering = ['-timestamp']


# class BookViewViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = BookView.objects.select_related('book').all()
#     serializer_class = BookViewSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['user', 'book']
#     search_fields = ['book__title']
#     ordering_fields = ['timestamp']
#     ordering = ['-timestamp']


# class SearchQueryViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = SearchQuery.objects.all()
#     serializer_class = SearchQuerySerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['user']
#     search_fields = ['query']
#     ordering_fields = ['timestamp']
#     ordering = ['-timestamp']


# class PurchaseEventViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = PurchaseEvent.objects.select_related('user', 'order').all()
#     serializer_class = PurchaseEventSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['user']
#     ordering_fields = ['timestamp', 'total_amount']
#     ordering = ['-timestamp']


class DashboardStatsView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        # Статистика за последние 30 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Общая статистика продаж
        sales_stats = OrderItem.objects.filter(
            order__created_at__gte=start_date
        ).aggregate(
            total_revenue=Sum(F('price') * F('quantity')),
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity')
        )
        
        # Статистика просмотров
        page_views = PageView.objects.filter(timestamp__gte=start_date).count()
        book_views = BookView.objects.filter(timestamp__gte=start_date).count()
        
        # Популярные поисковые запросы
        popular_searches = SearchQuery.objects.filter(
            timestamp__gte=start_date
        ).values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Топ книги по просмотрам
        top_books_views = BookView.objects.filter(
            timestamp__gte=start_date
        ).values('book__title').annotate(
            views=Count('id')
        ).order_by('-views')[:10]
        
        return Response({
            'sales': sales_stats,
            'views': {
                'page_views': page_views,
                'book_views': book_views
            },
            'popular_searches': list(popular_searches),
            'top_books_views': list(top_books_views)
        })
