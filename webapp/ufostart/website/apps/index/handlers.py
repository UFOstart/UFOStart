from ufostart.website.apps.models.procs import FindPublicNeeds


def index(context, request):
    result = FindPublicNeeds(request, {'Search': {'tags': ['Agile']}})
    return {}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")
