from collections import OrderedDict
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, Everyone, Authenticated, has_permission
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.models.procs import GetTemplateDetailsProc, GetAllCompanyTemplatesProc, GetCompanyProc


def canEdit(self): return has_permission('edit', self, self.request)
def canApprove(self): return has_permission('approve', self, self.request)


class BaseProjectContext(BaseContextMixin):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'create')]
    __auth_template__ = "ufostart:templates/auth/login.html"
    canEdit = reify(canEdit)
    canApprove = reify(canApprove)
    @property
    def site_title(self):
        return [self.displayName, self.company.display_name, self.request.globals.project_name]

    @reify
    def company(self):
        return self.__parent__.company


class TemplateContext(BaseProjectContext):
    @property
    def site_title(self):
        return [self.request.globals.project_name]
    def __init__(self, parent, name, template):
        self.__name__ = name
        self.__parent__ = parent
        self.template = template


class TemplatesRootContext(BaseProjectContext):
    @property
    def site_title(self):
        return [self.request.globals.project_name]
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, item):
        template = GetTemplateDetailsProc(self.request, {'key': item})
        if not template: raise KeyError()
        else:
            return TemplateContext(self, item, template)

    @reify
    def templates(self):
        return GetAllCompanyTemplatesProc(self.request)


class ApplicationContext(BaseProjectContext):
    displayType = "Application"
    displayName = ""

    def __init__(self, parent, name, acl, application):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.application = application

    @reify
    def round(self):
        return self.__parent__.round
    @reify
    def need(self):
        return self.__parent__.need


class NeedContext(BaseProjectContext):
    displayType = "Task"
    @property
    def displayProps(self):
        """
        only used for need edit, need_switch.js to find and replace names on switch
        """
        return 'data-entity-property="name"'
    @property
    def displayName(self):
        return self.need.name


    def __init__(self, parent, name, acl, need):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.need = need
    def __getitem__(self, item):
        return ApplicationContext(self, item, self.__acl__, self.need.applicationMap[item])

    @reify
    def round(self):
        return self.__parent__.round


class ProductContext(BaseProjectContext):
    displayType = "Product"
    @property
    def displayName(self):
        return self.product.name

    def __init__(self, parent, name, acl, product):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.product = product

    @reify
    def round(self):
        return self.__parent__.round


class FundingContext(BaseProjectContext):
    displayType = 'Funding'
    displayName = 'Invest'

    def __init__(self, parent, name, acl, funding):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.funding = funding

    @reify
    def round(self):
        return self.__parent__.round

class RoundContext(BaseProjectContext):
    displayType = "Round"
    @property
    def displayName(self):
        return self.round.Template.name

    def __init__(self, parent, name, acl, round):
        self.__parent__ = parent
        self.__name__ = name
        self.__acl__ = acl
        self.round = round
    def __getitem__(self, item):
        if item in ['productsetup', 'approve', 'reject', 'askforapproval']: raise KeyError()
        if item == 'product': return ProductContext(self, 'product', self.__acl__, self.round.Product)
        if item == 'funding': return FundingContext(self, 'funding', self.__acl__, self.round.Funding)
        return NeedContext(self, item, self.__acl__, self.round.needMap[item])

    def hasSuggestedNeeds(self):
        return len([need for need in self.round.Needs if need.added == False])> 0

    def groupedNeeds(self, n = 4, added = False):
        needs = [need for need in self.round.Needs if need.added == added]
        length = len(needs)
        if not length: return []
        result = OrderedDict()
        for i, need in enumerate(needs):
            l = result.setdefault(i % n, [])
            l.append(need)
        return result.values()


class CompanyContext(BaseProjectContext):
    displayType = "Company"
    @property
    def displayName(self):
        return self.company.name
    @property
    def site_title(self):
        return [self.company.display_name, self.request.globals.project_name]


    @reify
    def __acl__(self):
        mentors = [(Allow, 'u:%s' % u.token, 'approve') for u in self.company.Users if u.isMentor]
        founders = [(Allow, 'u:%s' % u.token, 'edit') for u in self.company.Users]
        return [(Allow, Authenticated, 'view')] + mentors + founders


    def __getitem__(self, item):
        try:
            return RoundContext(self, int(item), self.__acl__, self.company.currentRound)
        except ValueError:
            raise KeyError()

    @reify
    def company(self):
        company = GetCompanyProc(self.request, {'slug': self.__name__})
        if not company: raise HTTPNotFound()
        else: return company

class ProtoCompanyContext(BaseProjectContext):

    def __getitem__(self, item):
        return CompanyContext(self, item)

