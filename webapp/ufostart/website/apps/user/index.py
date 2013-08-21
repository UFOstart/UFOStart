from pyramid.httpexceptions import HTTPNotFound
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import RefreshProfileProc, FindPublicNeeds, FindPublicNeedsByLocation, GetNewProductsProc, GetProfileProc


def home(context, request):
    profile = context.profile
    best_match = FindPublicNeeds(request, {'Search': {'tags': profile.display_skills}})
    location = FindPublicNeedsByLocation(request)
    return {
        'best_match':best_match
        , 'isMyProfile': True
        , 'location_needs':location
    }



def user(context, request):
    profile = context.profile
    location = FindPublicNeedsByLocation(request)
    best_match = FindPublicNeeds(request, {'Search': {'tags': profile.display_skills}})
    return {'best_match':best_match, 'isMyProfile': False, 'location_needs':location}

def browse(context, request):
    return {}