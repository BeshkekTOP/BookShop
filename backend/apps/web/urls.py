from django.urls import path
from . import views
from . import admin_views
from . import buyer_views
from . import manager_views
from . import sales_views
from . import backup_views

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
    
    # Покупатель
    path('reviews/<int:book_id>/add/', buyer_views.add_review, name='add-review'),
    path('reviews/<int:book_id>/delete/', buyer_views.delete_review, name='delete-review'),
    path('profile/edit/', buyer_views.edit_profile, name='edit-profile'),
    path('checkout-detailed/', buyer_views.checkout_detailed, name='checkout-detailed'),
    path('checkout-success/<int:order_id>/', views.checkout_success, name='checkout-success'),
    path('orders/', buyer_views.orders_history, name='orders-history'),
    path('orders/<int:order_id>/', buyer_views.order_detail, name='order-detail'),
    path('orders/<int:order_id>/cancel/', buyer_views.cancel_order, name='cancel-order'),
    path('profile/logs/', buyer_views.user_activity_logs, name='user-activity-logs'),
    
    # Управление каталогом
    path('admin/books/', views.admin_books, name='admin-books'),
    path('admin/books/<int:pk>/edit/', views.admin_book_edit, name='admin-book-edit'),
    path('admin/books/<int:pk>/delete/', views.admin_book_delete, name='admin-book-delete'),
    path('admin/authors/', views.admin_authors, name='admin-authors'),
    path('admin/categories/', views.admin_categories, name='admin-categories'),
    
    # Админ-панель
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin-dashboard'),
    
    # Управление пользователями
    path('admin/users/', admin_views.admin_users_list, name='admin-users'),
    path('admin/users/create/', admin_views.admin_user_create, name='admin-user-create'),
    path('admin/users/<int:user_id>/', admin_views.admin_user_detail, name='admin-user-detail'),
    path('admin/users/<int:user_id>/change-role/', admin_views.admin_user_change_role, name='admin-user-change-role'),
    path('admin/users/<int:user_id>/activity/', admin_views.admin_user_activity_logs, name='admin-user-activity'),
    path('admin/users/<int:user_id>/delete/', admin_views.admin_user_delete, name='admin-user-delete'),
    
    # Управление остатками
    path('admin/inventory/', admin_views.admin_inventory, name='admin-inventory'),
    path('admin/inventory/<int:book_id>/update/', admin_views.admin_inventory_update, name='admin-inventory-update'),
    
    # Отчеты
    path('admin/reports/', admin_views.admin_reports, name='admin-reports'),
    path('admin/reports/export/', admin_views.admin_reports_export, name='admin-reports-export'),
    path('admin/reports/top-books/', admin_views.admin_reports_top_books, name='admin-reports-top-books'),
    path('admin/reports/user-activity/', admin_views.admin_reports_user_activity, name='admin-reports-user-activity'),
    
    # Логи
    path('admin/logs/', admin_views.admin_audit_logs, name='admin-logs'),
    
    # Резервные копии
    path('admin/backups/', backup_views.backup_list, name='admin-backups'),
    path('admin/backups/create/', backup_views.backup_create, name='admin-backup-create'),
    path('admin/backups/<str:filename>/download/', backup_views.backup_download, name='admin-backup-download'),
    path('admin/backups/<str:filename>/restore/', backup_views.backup_restore, name='admin-backup-restore'),
    path('admin/backups/<str:filename>/delete/', backup_views.backup_delete, name='admin-backup-delete'),
    
    # Менеджер
    path('manager/', manager_views.manager_dashboard, name='manager-dashboard'),
    path('manager/orders/', manager_views.manager_orders, name='manager-orders'),
    path('manager/orders/<int:order_id>/', manager_views.manager_order_detail, name='manager-order-detail'),
    path('manager/orders/<int:order_id>/update-status/', manager_views.manager_update_order_status, name='manager-update-order-status'),
    path('manager/statistics/', manager_views.manager_statistics, name='manager-statistics'),
    
    # Статистика продаж
    path('sales/', sales_views.sales_dashboard, name='sales-dashboard'),
    path('sales/reports/', sales_views.sales_reports, name='sales-reports'),
    path('manager/sales/', sales_views.manager_sales_stats, name='manager-sales-stats'),
]
