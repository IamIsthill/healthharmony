from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from healthharmony.app.settings import env


urlpatterns = [
    path("", include("healthharmony.base.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

if env.bool("INCLUDE_ADMIN", False):
    urlpatterns.append(path("admin/", admin.site.urls))
