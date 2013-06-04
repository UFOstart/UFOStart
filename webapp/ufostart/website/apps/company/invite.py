from hnc.forms.formfields import BaseForm
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from ufostart.website.apps.company.general import InviteeForm
from ufostart.website.apps.models.procs import InviteToCompanyProc


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

def confirm(context, request):
    return {}
