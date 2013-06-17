from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import RefreshProfileProc


@require_login()
def home(context, request):
    profile = RefreshProfileProc(request, {'token': context.user.token})
    return {'profile': profile}
