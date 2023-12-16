# urls.py

from django.urls import path
from .views import CustomUserUpdateView, UserCreateView, UserListView,UserCreateCordiGeneView,UserListViewCordiGen,UserListViewCordiPromo,UserCreateViewPromotor,seccionlist,SeccionCreateView, update_user_statusCordiGene,\
SeccionUpdateView, update_user_statusPromotor,callesList,SeccionDetailView
from django.contrib.auth import views as auth_views


urlpatterns = [
    # ... tus otras urls
    path('update_profile/', CustomUserUpdateView.as_view(), name='update_profile'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html'), name='change_password'),
    path('change_password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html'), name='password_change_done'),
   
    # Administradores
    path('registrar-usuario/', UserCreateView.as_view(), name='register_user_cordi'),
    path('lista-usuarios/', UserListView.as_view(), name='users_list'),

    # Coordinadores generales
    path('registrar-usuario-coordinador-general/', UserCreateCordiGeneView.as_view(), name='register_user_cordi_general'),
    path('lista-usuarios-coordinador-general/', UserListViewCordiGen.as_view(), name='users_list_cordi_gene'),

    # Concsultar 
    path('consultar-usuarios-promotor/', UserListViewCordiPromo.as_view(), name='UserListViewCordiPromo'),



    path('registrar-usuario-promotor/', UserCreateViewPromotor.as_view(), name='UserCreateViewPromotor'),

    path('secciones/', seccionlist.as_view(), name='seccion_list'),
    path('crear-secciones/', SeccionCreateView.as_view(), name='seccion_create'),
    path('update-secciones/<int:pk>/', SeccionUpdateView.as_view(), name='seccion_update'),
    path('seccion/<int:pk>/', SeccionDetailView.as_view(), name='detalle_seccion'),





    #--------------------------------- ACTUALIZAR STATUS PARA EL LOGIN ----------------------------
    path('update_user_status_general/<int:user_id>/', update_user_statusCordiGene, name='update_user_status_gene'),
    path('update_user_status_promotor/<int:user_id>/', update_user_statusPromotor, name='update_user_status_promotor'),

]
