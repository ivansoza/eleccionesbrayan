from django.contrib import admin
from django.urls import path, include
from .views import CreatePromovidoNuevo, EliminarPromovido, EliminarProspecto, ListaPromovidosNuevo, UpdatePromovidoNuevo, UpdateProspectoNuevo, estadisticasGenerales,CreateProspectoNuevo,ListaProspectosNuevo,MapaProspectosPromovidosView
from .views import   EstadisticasGeneralesView, EstadisticasSoliView
from .views import ProspectoUpdateView, ListCumple, Felicitar, PromovidosLista, verificarPromovidos, CalleListView
from .views import verificar_numero_ine,obtener_calles, CalleDetailView,SeccionListView,SeccionDetailView, votosSeguros, ListaVotoSeguro, MapaVotosSegurosView,MapaVerificadosView

urlpatterns = [
    path("crearPromovidos/", CreatePromovidoNuevo.as_view(), name='crearPromovidos'),
    path('promovido/actualizar/<int:pk>/', UpdatePromovidoNuevo.as_view(), name='actualizar_promovido'),
    path('lista_promovidos/', ListaPromovidosNuevo.as_view(), name='lista_promovidos'),
    path('eliminar/<int:pk>/', EliminarPromovido.as_view(), name='eliminar_promovido'),



    path('lista_prospectos/', ListaProspectosNuevo.as_view(), name='lista_prospectos'),
    path('prospecto/actualizar/<int:pk>/', UpdateProspectoNuevo.as_view(), name='UpdateProspectoNuevo'),
    path('eliminar-prospecto/<int:pk>/', EliminarProspecto.as_view(), name='EliminarProspecto'),

    path('lista_voto_seguro/', ListaVotoSeguro.as_view(), name='lista_votos_seguros'),

    path("mapa/", MapaProspectosPromovidosView.as_view(), name='mapa'),
    path("mapa/votos-seguros/", MapaVotosSegurosView.as_view(), name='mapa-voto-seguro'),

    path("mapa/votos-verificados/", MapaVerificadosView.as_view(), name='MapaVerificadosView'),



    path("crear-prospecto/", CreateProspectoNuevo.as_view(), name='crearProspectoNuevo'),
    path('prospecto/actualizar/<int:pk>/', ProspectoUpdateView.as_view(), name='prospecto_actualizar'),
    path('verificar_numero_ine/', verificar_numero_ine, name='verificar_numero_ine'),
    path("lista-cumple/", ListCumple.as_view(), name='lista-cumple'),
    path('felicitar/<int:pk>/', Felicitar.as_view(), name='felicitar'),
    path('obtener-calles', obtener_calles, name='obtener_calles'),
    path("lista-promovidos-verificar/", PromovidosLista.as_view(), name='lista-promovidos-verificar'),
    path('verificar/<int:pk>/', verificarPromovidos.as_view(), name='verificar'),



    # -------------------  ESTADISTICAS --------------

    path('estadisticas/', estadisticasGenerales.as_view(), name='estadisticas'),
    path('estadisticasDona/<int:pk>/', EstadisticasGeneralesView.as_view(), name='estadisticasDona'),
    path('estadisticasSolicitud/', EstadisticasSoliView.as_view(), name='estadisticasSolicitud'),
    path('estadisticas/calles/', CalleListView.as_view(), name='lista_calles'),
    path('estadisticas/detalle/calles/<int:pk>/<str:status>/', CalleDetailView.as_view(), name='detalle_calle_con_status'),
    path('estadisticas/detalle/calles/<int:pk>/', CalleDetailView.as_view(), name='detalle_calle'),
    path('estadisticas/secciones/', SeccionListView.as_view(), name='seccion-list'),
    
    
    path('estadisticas/detalle/seccion/<int:pk>/<str:status>/', SeccionDetailView.as_view(), name='detalle_seccion_con_status'),
    path('estadisticas/detalle/seccion/<int:pk>/', SeccionDetailView.as_view(), name='detalle_seccion'),
    path('estadisticas/voto_seguro/', votosSeguros.as_view(), name='voto_seguro'),


]  