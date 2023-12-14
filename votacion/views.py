from django.shortcuts import render
from promovido.models import prospecto
from datetime import datetime, date
from django.views.generic import CreateView, TemplateView, ListView, UpdateView

class VotosLista(ListView):
    template_name = 'listVotantes.html'
    context_object_name = 'prospectos'
    model = prospecto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Contar el número de prospectos con status 'Promovido' y 'Verificado'
        num_promovidos = prospecto.objects.filter(status='Promovido').count()
        num_verificados = prospecto.objects.filter(status='Verificado').count()
        num_rechazados = prospecto.objects.filter(status='Rechazado').count()

        context['num_promovidos'] = num_promovidos
        context['num_verificados'] = num_verificados
        context['num_rechazados'] = num_rechazados
        context['navbar'] = 'votos'  
        context['seccion'] = 'listvotantes' 

        return context

    def get_queryset(self):
        today = datetime.now().date()
        queryset = prospecto.objects.filter(status='Verificado')
     
        for promovido in queryset:
            edad = today.year - promovido.fechaNacimiento.year - (
                (today.month, today.day) < (promovido.fechaNacimiento.month, promovido.fechaNacimiento.day)
            )
            setattr(promovido, 'edad', edad)

        return queryset