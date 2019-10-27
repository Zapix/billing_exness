from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework.schemas import get_schema_view

from billing_exness.openapi.schema import BillingExnessSchemaGenerator

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="pages/home.html"), name="home"
    ),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("billing_exness.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("api/v1/", include("billing_exness.api.v1.urls", namespace="api_v1")),
    path(
        "openapi/v1/",
        TemplateView.as_view(template_name="swagger-ui.html")
    ),
    path(
        "openapi/v1/schema/",
        get_schema_view(
            title="Billing Exness",
            description="Test billing api",
            version="1.0.0'",
            url='/api/v1/',
            urlconf='billing_exness.api.v1.urls',
            generator_class=BillingExnessSchemaGenerator
        ),
        name='openapi_v1_schema'
    )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls))
        ] + urlpatterns
