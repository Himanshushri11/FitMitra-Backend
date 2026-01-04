from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/fitness/", include("fitness.urls")),
    path("api/ai/", include("ai.urls")),
    path("api/explore/", include("explore.urls")),
    path("api/admin-panel/", include("admin_panel.urls")),
    path('api/support/', include('support.urls')),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
