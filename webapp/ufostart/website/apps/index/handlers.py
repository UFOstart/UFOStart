from ufostart.website.apps.models.procs import FindPublicNeeds


def index(context, request):
    if not context.user.isAnon():
        route, args, kwargs = context.getPostLoginUrlParams()
        if route: request.fwd(route, *args, **kwargs)
    else:
        result = FindPublicNeeds(request, {'Search': {'tags': ['office']}})
    return {}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")
