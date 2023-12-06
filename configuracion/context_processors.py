from .models import CandidatoConfig

def candidato_config_processor(request):
    config = CandidatoConfig.objects.first()  # Obtiene la primera instancia, o None si no existe
    return {'candidato_config': config}
