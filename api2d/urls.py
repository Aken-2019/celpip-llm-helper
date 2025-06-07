from django.urls import path
from .views import ApiKeyView, home_page_view, ApiKeyDeleteView, upload_mp3, get_credit_info

app_name = 'api2d'

urlpatterns = [
    path("", home_page_view, name='home'),
    path("api-key/", ApiKeyView.as_view(), name='api-key'),
    path("api-key/delete/", ApiKeyDeleteView.as_view(), name='api-key-delete'),
    path("celpip/speaking/", upload_mp3, name='celpip-speaking'),
]