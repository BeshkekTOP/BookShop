from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('home/', views.home, name='home-page'),
    path('catalog/', views.catalog_list, name='catalog'),
    path('books/<int:pk>/', views.book_detail, name='book-detail'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin/books/', views.admin_books, name='admin-books'),
    path('admin/books/<int:pk>/edit/', views.admin_book_edit, name='admin-book-edit'),
    path('admin/books/<int:pk>/delete/', views.admin_book_delete, name='admin-book-delete'),
    path('admin/authors/', views.admin_authors, name='admin-authors'),
    path('admin/categories/', views.admin_categories, name='admin-categories'),
]
