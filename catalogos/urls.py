# urls.py

from django.urls import path
from .views import CalleCreateView, crearPublicidad, mapaPublicidad, mostrar_mapa
from .views import postal_code_view,postal_code_view_test,pruebacp, callesList

urlpatterns = [
    # ... tus otras urls
    
    path('crear-publicidad/', crearPublicidad.as_view(), name='crear-publicidad'),
    path('mapapublicidad/', mapaPublicidad.as_view(), name='mapapublicidad'),
    path('postal-code/<slug:postal_code>/', postal_code_view, name='postal_code_view'),
    path('postal-code2/<slug:postal_code>/', postal_code_view_test, name='postal_code_view2'),
    path('postal/', pruebacp, name='postal_code_view3'),

    path('calles/', callesList.as_view(), name='calle_list'),
    path('calle/create/', CalleCreateView.as_view(), name='calle_create'),
    path('mostrar_mapa/<int:calle_id>/', mostrar_mapa, name='mostrar_mapa'),

]
