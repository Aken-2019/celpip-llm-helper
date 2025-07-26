from django.urls import path
from .views import (
    ApiKeyView,
    ApiKeyDeleteView,
    upload_mp3,
    celpip_writting,
    celpip_speaking,
)

app_name = "api2d"

urlpatterns = [
    path("api-key/", ApiKeyView.as_view(), name="api-key"),
    path("api-key/delete/", ApiKeyDeleteView.as_view(), name="api-key-delete"),
    path("celpip/speaking/", upload_mp3, name="celpip-speaking"),
    path("celpip/writting/", celpip_writting, name="celpip-writing"),
    path("celpip/speaking-rev/", celpip_speaking, name="celpip-speaking-rev"),
]
