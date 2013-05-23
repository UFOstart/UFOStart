from pyramid.decorator import reify

class BaseHandler(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

class RootContext(object):
    app_label = 'root'
    root_statics = '/static/'
    static_prefix = '/static/'
    def __init__(self, request):
        self.request = request

    def is_allowed(self, request):
        return True

    @reify
    def settings(self):
        return getattr(self.request.globals, self.app_label)