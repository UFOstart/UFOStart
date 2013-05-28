def index(context, request):
    if not context.user.isAnon():
        route, args, kwargs = context.getPostLoginUrlParams()
        request.fwd(route, *args, **kwargs)
    return {}
