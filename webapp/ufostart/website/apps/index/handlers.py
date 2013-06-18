from ufostart.website.apps.models.procs import FindPublicNeeds, GetPopularNeeds, GetNewProductsProc


def index(context, request):
    tag_needs = FindPublicNeeds(request, {'Search': {'tags': ['Agile']}})
    popular_needs = GetPopularNeeds(request)
    new_products = GetNewProductsProc(request)
    return {'popular_needs':popular_needs[:4], 'needs_close_by': tag_needs}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")
