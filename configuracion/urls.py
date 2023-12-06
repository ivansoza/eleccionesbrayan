# urls.py

from django.urls import path
from .views import ConfiguracionView, check_config_and_redirect, ConfiguracionUpdateView
urlpatterns = [
    path("", ConfiguracionView.as_view(), name="configuracion"),

    path('config/check/', check_config_and_redirect, name='check_config'),
    path('config/create/', ConfiguracionView.as_view(), name='ruta_create_view'),
    path('config/update/<int:pk>/', ConfiguracionUpdateView.as_view(), name='ruta_update_view'),
]
