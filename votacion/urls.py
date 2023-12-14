from django.contrib import admin
from django.urls import path, include
from .views import VotosLista


urlpatterns = [
    path("lista-votos/", VotosLista.as_view(), name='lista-votos'),



]