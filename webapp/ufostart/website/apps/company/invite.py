from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, EmailField, REQUIRED, HiddenField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage, GenericErrorMessage
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import InviteToCompanyProc, GetInviteDetailsProc, AcceptInviteProc, RefreshProfileProc


def InviteCompanyForm(role_):
    class InviteForm(BaseForm):
        id="InviteCompany_{}".format(role_)
        label = role_.title().replace("_", " ")
        role = role_
        fields = [
            StringField("name", "Name", REQUIRED)
            , EmailField("email", "email address", REQUIRED)
            , HiddenField("role")
        ]
        @classmethod
        def on_success(cls, request, values):
            user = request.root.user
            company = request.root.company

            values['invitorToken'] = user.token
            values['invitorName'] = user.name
            values['companySlug'] = company.slug

            InviteToCompanyProc(request, {'Invite': [values]})

            request.session.flash(GenericSuccessMessage("You successfully invited {name} to your company!".format(**values)), "generic_messages")
            return {'success':True, 'redirect': request.fwd_url("website_company_company", slug = request.matchdict['slug'])}
    return InviteForm

class InviteCompanyHandler(FormHandler):
    forms = [InviteCompanyForm(role) for role in ['MENTOR', 'FOUNDER', 'TEAM_MEMBER']]

    def pre_fill_values(self, request, result):
        company = request.root.company
        result['company'] = company
        return super(InviteCompanyHandler, self).pre_fill_values(request, result)

class AddMentorHandler(FormHandler):
    form = InviteCompanyForm('MENTOR')
    def pre_fill_values(self, request, result):
        company = request.root.company
        result['company'] = company
        return super(AddMentorHandler, self).pre_fill_values(request, result)



def answer(context, request):
    token = request.matchdict['token']
    invite = None
    try:
        invite = GetInviteDetailsProc(request, {'inviteToken': token})
    except DBNotification, e:
        pass
    if not invite:
        request.session.flash(GenericErrorMessage("Invalid Token, please check your email and link!"), "generic_messages")
        request.fwd("website_index")
    return {'invite': invite}

@require_login('ufostart:website/templates/auth/login.html')
def confirm(context, request):
    token = request.matchdict['token']

    invite = GetInviteDetailsProc(request, {'inviteToken': token})
    AcceptInviteProc(request, {'inviteToken':token, 'userToken': context.user.token})
    RefreshProfileProc(request, {'token': context.user.token})
    request.fwd("website_company_company", slug = invite.companySlug)



def login(context, request, profile):
    request.fwd("website_invite_answer", token = request.matchdict['token'])


