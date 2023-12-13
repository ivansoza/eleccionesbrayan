from django.contrib import admin
from django.urls import path, include
from .views import CreatePromovidoNuevo, createUbicacion, ListaPromovidosNuevo, createProspecto, updateProspecto, estadisticasGenerales,CreateProspectoNuevo,ListaProspectosNuevo,MapaProspectosPromovidosView
from .views import guardar_ubicacion, mapas, EstadisticasGeneralesView, EstadisticasSoliView
from .views import ProspectoUpdateView, ListCumple, Felicitar, PromovidosLista, verificarPromovidos
from .views import verificar_numero_ine,obtener_calles

urlpatterns = [
    path("crearPromovidos/", CreatePromovidoNuevo.as_view(), name='crearPromovidos'),
    path("crearUbicacionPro/<int:promovido_id>/", createUbicacion.as_view(), name='crearUbicacionPro'),
    path('lista_promovidos/', ListaPromovidosNuevo.as_view(), name='lista_promovidos'),
    path("crearProspecto/", createProspecto.as_view(), name='crearProspecto'),
    path('lista_prospectos/', ListaProspectosNuevo.as_view(), name='lista_prospectos'),
    path('promoverProspectos/<int:pk>', updateProspecto.as_view(), name='promoverProspectos'),
   
    path("guardar_ubicacion", guardar_ubicacion, name='guardar_ubicacion'),
    path("mapa/", MapaProspectosPromovidosView.as_view(), name='mapa'),
    path('estadisticas/', estadisticasGenerales.as_view(), name='estadisticas'),
    path('estadisticasDona/<int:pk>/', EstadisticasGeneralesView.as_view(), name='estadisticasDona'),
    path('estadisticasSolicitud/', EstadisticasSoliView.as_view(), name='estadisticasSolicitud'),

    path("crear-prospecto/", CreateProspectoNuevo.as_view(), name='crearProspectoNuevo'),
    path('prospecto/actualizar/<int:pk>/', ProspectoUpdateView.as_view(), name='prospecto_actualizar'),
    path('verificar_numero_ine/', verificar_numero_ine, name='verificar_numero_ine'),
    path("lista-cumple/", ListCumple.as_view(), name='lista-cumple'),
    path('felicitar/<int:pk>/', Felicitar.as_view(), name='felicitar'),
    path('obtener-calles', obtener_calles, name='obtener_calles'),
    path("lista-promovidos-verificar/", PromovidosLista.as_view(), name='lista-promovidos-verificar'),
    path('verificar/<int:pk>/', verificarPromovidos.as_view(), name='verificar'),


]  