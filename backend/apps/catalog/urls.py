from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, AuthorViewSet, BookViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')

urlpatterns = router.urls

















