from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path,
)

from shop.views import register


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "accounts/",
        include(
            "django.contrib.auth.urls"
        ),
    ),
    path(
        "register/",
        register,
        name="register",
    ),
    path(
        "",
        include("shop.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )