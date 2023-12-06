


def profile_completion(request):
    user_profile_complete = True  # Cambiar por la lógica real de comprobación
    if request.user.is_authenticated:
        user_profile_complete = request.user.profile_complete()
    return {'user_profile_complete': user_profile_complete}


# Agregar un clasificador de grupos 

def user_groups(request):
    groups = [group.name for group in request.user.groups.all()]
    return {'user_groups': groups}

def group_context(request):
    context = {
        'es_administrador': request.user.groups.filter(name='Administrador').exists(),
        'es_coordinador_area': request.user.groups.filter(name='Coordinador de Area').exists(),
        'es_coordinador_general': request.user.groups.filter(name='Coordinador General').exists(),
        'es_coordinador_seccion': request.user.groups.filter(name='Coordinador Sección').exists(),
        'es_promotor': request.user.groups.filter(name='Promotor').exists(),
        'es_candidato': request.user.groups.filter(name='Candidato').exists(),
    }
    return context