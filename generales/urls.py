from django.urls import path, include
from .views import menu, home, CustomLoginView, exit, datos_promovidos,templeteDenegado,ubicacion_primera_seccion

from django.contrib.auth.views import LoginView


from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', home, name="home"),
    path('menu/', menu, name='menu'),
    path('logout/', exit, name="exit"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('obtener-promovidos/', datos_promovidos, name='datos_promovidos'),
        
    path('ubicacion-primera-seccion/', ubicacion_primera_seccion, name='primera-seccion'),

    path('denegado/', templeteDenegado.as_view(), name='templeteDenegado'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)