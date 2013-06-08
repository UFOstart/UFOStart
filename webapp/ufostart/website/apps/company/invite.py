from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage, GenericErrorMessage
from ufostart.website.apps.company.general import InviteeForm
from ufostart.website.apps.models.procs import InviteToCompanyProc, GetInviteDetailsProc, AcceptInviteProc


class InviteCompanyForm(BaseForm):
    id="InviteCompany"
    label = ""
    fields=[
        InviteeForm('Invitees')
    ]
    @classmethod
    def on_success(cls, request, values):
        data = []
        user = request.root.user
        company = request.root.company
        for inv in values.get('Invitees'):
            inv['invitorToken'] = user.token
            inv['invitorName'] = user.name
            inv['companySlug'] = company.slug
            data.append(inv)
        InviteToCompanyProc(request, {'Invite': data})
        request.session.flash(GenericSuccessMessage("You successfully invited {} users to your company!".format(len(data))), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_company", slug = request.matchdict['slug'])}

class InviteCompanyHandler(FormHandler):
    form = InviteCompanyForm

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

def confirm(context, request):
    token = request.matchdict['token']

    invite = GetInviteDetailsProc(request, {'inviteToken': token})
    AcceptInviteProc(request, {'inviteToken':token, 'userToken': context.user.token})

    request.fwd("website_company", slug = invite.companySlug)



def login(context, request, profile):
    request.fwd("website_invite_answer", token = request.matchdict['token'])


