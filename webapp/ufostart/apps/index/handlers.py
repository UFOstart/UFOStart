from ufostart.apps.models.procs import FindPublicNeeds, GetPopularNeeds, GetNewProductsProc, FindPublicNeedsByLocation


def index(context, request):
    popular_needs = GetPopularNeeds(request)
    location = FindPublicNeedsByLocation(request)
    products = GetNewProductsProc(request)
    return {'popular_needs':popular_needs, 'needs_close_by': location, 'products': products}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")
