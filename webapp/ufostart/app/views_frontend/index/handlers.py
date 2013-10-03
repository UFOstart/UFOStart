from ufostart.models.procs import FindPublicNeeds, GetPopularNeeds, GetNewProductsProc, FindPublicNeedsByLocation


def index(context, request):
    return {}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd(request.root)
