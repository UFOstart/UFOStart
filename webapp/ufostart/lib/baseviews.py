from pyramid.decorator import reify
from hnc.forms.formfields import BaseForm as BF, GRID_BS3



class BaseForm(BF):
    grid = GRID_BS3
    @classmethod
    def cancel_url(cls, request):
        return request.rld_url()


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


class BaseContextMixin(object):
    __name__ = None
    __parent__ = None

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    @property
    def request(self):
        return self.__parent__.request
    @property
    def user(self):
        return self.__parent__.user


    #=================================================== Hierarchy Helpers =============================================



    @reify
    def __hierarchy__(self):
        result = []
        p = self
        while p:
            result.append(p)
            p = p.__parent__
        return result[::-1]


    def get_main_area(self):
        return self.__hierarchy__[1] if len(self.__hierarchy__)>1 else None
    main_area = reify(get_main_area)

    def get_area_url(self, *args, **kwargs):
        return self.request.resource_url(self.main_area, *args, **kwargs)

    def get_sub_area(self):
        return self.__hierarchy__[2] if len(self.__hierarchy__)>2 else None
    sub_area = reify(get_sub_area)


