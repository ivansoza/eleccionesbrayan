# urls.py

from django.urls import path
from .views import crearPublicidad, mapaPublicidad
from .views import postal_code_view,postal_code_view_test,pruebacp

urlpatterns = [
    # ... tus otras urls
    
    path('crear-publicidad/', crearPublicidad.as_view(), name='crear-publicidad'),
    path('mapapublicidad/', mapaPublicidad.as_view(), name='mapapublicidad'),
    path('postal-code/<slug:postal_code>/', postal_code_view, name='postal_code_view'),
    path('postal-code2/<slug:postal_code>/', postal_code_view_test, name='postal_code_view2'),
    path('postal/', pruebacp, name='postal_code_view3'),


]
