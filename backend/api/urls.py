from django.urls import include, path

urlpatterns = [
    path("", include("backend.api.docs")),
    path("auth/", include("backend.apps.users.urls")),
    path("", include("backend.apps.catalog.urls")),
    path("", include("backend.apps.orders.urls")),
    path("", include("backend.apps.reviews.urls")),
    path("", include("backend.apps.analytics.urls")),
]
