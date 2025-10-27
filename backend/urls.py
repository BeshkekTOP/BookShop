from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('', include('backend.apps.web.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("backend.api.urls")),
]

# Обслуживание статики и медиафайлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # В production всегда обслуживаем статику (для доступа без nginx)
    urlpatterns += [
        path(f'{settings.STATIC_URL.lstrip("/")}<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
        path(f'{settings.MEDIA_URL.lstrip("/")}<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

