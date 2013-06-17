from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, EmailField, REQUIRED
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage, GenericErrorMessage
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import InviteToCompanyProc, GetInviteDetailsProc, AcceptInviteProc


class InviteCompanyForm(BaseForm):
    id="InviteCompany"
    label = ""
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "email address", REQUIRED)
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

class InviteCompanyHandler(FormHandler):
    form = InviteCompanyForm

    def pre_fill_values(self, request, result):
        company = request.root.company
        result['company'] = company
        angelListId = company.angelListId if company.angelListId != 'asdfasdf' else ''
        angelListToken = company.angelListToken

        if angelListId:
            networkSettings = request.root['angellist']
            company = networkSettings.getCompanyData(angelListId, angelListToken)
            if company:
                roles = filter(lambda x: 'founder' in x.role, networkSettings.getCompanyRoles(angelListId, angelListToken))
                result.update({'al_company': company, 'company_roles': roles})

        return super(InviteCompanyHandler, self).pre_fill_values(request, result)


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

    request.fwd("website_company_company", slug = invite.companySlug)



def login(context, request, profile):
    request.fwd("website_invite_answer", token = request.matchdict['token'])


