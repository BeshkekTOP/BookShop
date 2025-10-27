from datetime import datetime
from django.db.models import Sum, F
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, views
from rest_framework.response import Response
import csv

from backend.apps.orders.models import OrderItem


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
