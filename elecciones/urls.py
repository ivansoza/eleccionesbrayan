"""
URL configuration for elecciones project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django_postalcodes_mexico import urls as django_postalcodes_mexico_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('generales.urls')),
    path("promovido/", include('promovido.urls')),

    path("actualizar/", include('usuarios.urls')),

    path("promovido/", include('promovido.urls')),

    path("catalogos/", include('catalogos.urls')),
    path("agenda/", include('agenda.urls')),
    path("configuracion/", include('configuracion.urls')),
    path('postal-code/', include(django_postalcodes_mexico_urls)),


]
