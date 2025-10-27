from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'book').all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['book', 'user', 'is_moderated', 'rating']
    search_fields = ['text', 'book__title', 'user__username']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list' and not self.request.user.is_staff:
            # Показываем только модерированные отзывы для обычных пользователей
            queryset = queryset.filter(is_moderated=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_moderated=False)

    def perform_update(self, serializer):
        # Пользователь может редактировать только свои отзывы
        if serializer.instance.user != self.request.user and not self.request.user.is_staff:
            return Response(
                {"detail": "Вы можете редактировать только свои отзывы"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        # Пользователь может удалять только свои отзывы
        if instance.user != self.request.user and not self.request.user.is_staff:
            return Response(
                {"detail": "Вы можете удалять только свои отзывы"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_moderated = True
        review.save()
        return Response(ReviewSerializer(review).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.is_moderated = False
        review.save()
        return Response(ReviewSerializer(review).data)




