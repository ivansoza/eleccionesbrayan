from django.urls import path, include
from .views import   ListaTodos, home, CustomLoginView, exit, datos_promovidos,templeteDenegado,ubicacion_primera_seccion,MenuView,send_sms_view

from django.contrib.auth.views import LoginView


from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', home, name="home"),
    path('menu/', MenuView.as_view(), name='menu'),
    path('logout/', exit, name="exit"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('obtener-promovidos/', datos_promovidos, name='datos_promovidos'),
        
    path('ubicacion-primera-seccion/', ubicacion_primera_seccion, name='primera-seccion'),

    path('denegado/', templeteDenegado.as_view(), name='templeteDenegado'),
    path('send_sms/', send_sms_view, name='send_sms'),
    path('buscador/', ListaTodos.as_view(), name='buscador'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)