from ufostart.website.apps.auth.social import require_login


@require_login()
def home(context, request):
    return {}
