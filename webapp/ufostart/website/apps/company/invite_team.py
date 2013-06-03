from hnc.forms.formfields import MultipleFormField, StringField, EmailField, REQUIRED, BaseForm
from hnc.forms.handlers import FormHandler


class InviteeForm(MultipleFormField):
    template = 'ufostart:website/templates/company/controls/invitee.html'
    add_more_link_label = "Add Invitee"
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "email address", REQUIRED)
    ]


class InviteCompanyForm(BaseForm):
    id="InviteCompany"
    label = ""
    fields=[
        InviteeForm('Invitees')
    ]
    @classmethod
    def on_success(cls, request, values):
            return {'success':True, 'redirect': request.fwd_url("website_company")}

class InviteCompanyHandler(FormHandler):
    form = InviteCompanyForm


