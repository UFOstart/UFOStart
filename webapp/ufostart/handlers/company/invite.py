from operator import attrgetter
from hnc.apiclient.backend import DBNotification
from hnc.forms.messages import GenericErrorMessage
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationStringFactory
from pyramid.security import Allow, Everyone, Authenticated
from ufostart.handlers.company.__resources__ import RoundContext, ProtoCompanyContext, CompanyContext, BaseProjectContext
from ufostart.models.procs import AcceptInviteProc, RefreshProfileProc, GetCompanyProc, GetInviteDetailsProc

_ = TranslationStringFactory("uforeloaded")



class ProtoInviteContext(BaseProjectContext):
    __acl__ = [(Allow, Everyone, 'view'), (Allow, Authenticated, 'join')]
    __auth_template__ = "ufostart:templates/company/invite_confirm.html"
    def __init__(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, item):
        invite = self.getInvite(item)
        if invite.Need:
            return InviteNeedContext(self, item, invite)
        else:
            return InviteContext(self, item, invite)


    def getInvite(self, token):
        invite = None
        try:
            invite = GetInviteDetailsProc(self.request, {'inviteToken': token})
        except DBNotification, e:
            pass
        if not invite:
            self.request.session.flash(GenericErrorMessage("Invalid Token, please check your email and link!"), "generic_messages")
            raise HTTPFound(self.request.root.home_url)
        return invite


class InviteContext(RoundContext):
    canEdit = False
    canApprove = False

    displayType = "Company"
    @property
    def displayName(self):
        return self.company.name
    @property
    def site_title(self):
        return [self.company.display_name, self.request.globals.project_name]

    __auth_template__ = "ufostart:templates/company/invite_confirm.html"

    def __init__(self, parent, name, invite):
        self.__name__ = name
        self.__parent__ = parent
        self.invite = invite
        if self.company.isMember(self.request.root.user.token):
            self.after_action_fwd()

    def after_action_fwd(self):
        raise HTTPFound(self.request.root.round_url(self.company.slug, '1'))

    @reify
    def company(self):
        company = GetCompanyProc(self.request, {'slug': self.invite.companySlug})
        if not company: raise HTTPNotFound()
        else: return company

    @reify
    def round(self):
        return self.company.Round

    @reify
    def mockContext(self):
        root = self.request.root
        protoCtxt = ProtoCompanyContext(root,'c')
        companyCtxt = CompanyContext(protoCtxt, self.company.slug)
        return RoundContext(companyCtxt,'1', companyCtxt.__acl__, self.company.Round)


class InviteNeedContext(InviteContext):
    __auth_template__ = "ufostart:templates/company/invite_need_confirm.html"

    @reify
    def need(self):
        return self.round.needMap[self.invite.Need.slug]

    def after_action_fwd(self):
        raise HTTPFound(self.request.root.need_url(self.invite.companySlug, self.need.slug))



def invite_landing(context, request): return {}

def confirm(context, request):
    AcceptInviteProc(request, {'inviteToken':context.__name__, 'userToken': request.root.user.token})
    RefreshProfileProc(request, {'token': request.root.user.token})
    raise HTTPFound(context.after_action_fwd())

def reject(context, request):
    raise HTTPFound(context.after_action_fwd())