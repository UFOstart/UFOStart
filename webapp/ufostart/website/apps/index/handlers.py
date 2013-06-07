def index(context, request):
    if not context.user.isAnon():
        route, args, kwargs = context.getPostLoginUrlParams()
        request.fwd(route, *args, **kwargs)
    return {}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")
