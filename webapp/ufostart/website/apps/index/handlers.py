def index(context, request):
    if not context.user.isAnon():
        request.fwd("website_company_setup_basic")
    return {}
