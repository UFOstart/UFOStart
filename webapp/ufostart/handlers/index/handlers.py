from pyramid.httpexceptions import HTTPNotFound
from ufostart.models.procs import AdminPageGetProc


def index(context, request):
    return {}


def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd(request.root)


def content_view(context, request):
    try:
        return {'page':AdminPageGetProc(request, {'url':'/'.join(request.subpath)})}
    except KeyError, e:
        raise HTTPNotFound()