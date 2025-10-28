from rest_framework import serializers
from .models import PageView, BookView, SearchQuery, PurchaseEvent


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = (
            "id", "user", "session_key", "path", "ip_address", 
            "user_agent", "referer", "timestamp"
        )
        read_only_fields = ("timestamp",)


class BookViewSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BookView
        fields = (
            "id", "user", "book", "book_title", "session_key", 
            "ip_address", "timestamp"
        )
        read_only_fields = ("timestamp",)


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = (
            "id", "user", "query", "results_count", "session_key", 
            "ip_address", "timestamp"
        )
        read_only_fields = ("timestamp",)


class PurchaseEventSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)

    class Meta:
        model = PurchaseEvent
        fields = (
            "id", "user", "order", "order_id", "total_amount", 
            "items_count", "timestamp"
        )
        read_only_fields = ("timestamp",)


















