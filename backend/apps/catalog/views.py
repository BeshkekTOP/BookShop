from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import Category, Author, Book
from .serializers import (
    CategorySerializer,
    AuthorSerializer,
    BookSerializer,
    BookWriteSerializer,
)


class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_staff


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["last_name", "first_name"]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("category").all()
    permission_classes = [ReadOnlyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "category": ["exact"],
        "price": ["gte", "lte"],
        "rating": ["gte", "lte"],
    }
    search_fields = ["title", "isbn", "book_authors__author__first_name", "book_authors__author__last_name"]
    ordering_fields = ["title", "price", "rating", "created_at"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BookWriteSerializer
        return BookSerializer




