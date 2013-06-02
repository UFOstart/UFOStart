from hnc.forms.formfields import BaseForm, StringField, TextareaField, REQUIRED, MultipleFormField, EmailField
from hnc.forms.handlers import FormHandler
from ufostart.lib.tools import group_by_n
from ufostart.website.apps.company.forms import RoundSetupForm, CompanyTemplateForm
from ufostart.website.apps.models.company import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, GetAllNeedsProc, GetRoundProc


class SetupCompanyForm(BaseForm):
    id="SetupCompany"
    label = ""
    fields=[
        StringField("name", "Name", REQUIRED)
        , TextareaField("description", "Description", REQUIRED, input_classes="x-high")
    ]
    @classmethod
    def on_success(cls, request, values):
        return {'success':True, 'redirect': request.fwd_url("website_company_invite")}

class SetupCompanyHandler(FormHandler):
    form = SetupCompanyForm




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







# NOTE: DEPRECATED


class BasicHandler(FormHandler):
    form = CompanyTemplateForm

    def __init__(self, context=None, request=None):
        # if context.user.Company.Template: request.fwd("website_company_setup_round")
        super(BasicHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        templates = GetAllCompanyTemplatesProc(request)
        result['templates'] = group_by_n(templates)
        return super(BasicHandler, self).pre_fill_values(request, result)

class RoundHandler(FormHandler):
    form = RoundSetupForm
    def pre_fill_values(self, request, result):
        templateName = self.context.user.Company.Template.name
        template = GetTemplateDetailsProc(request, {'name': templateName})
        needs = GetAllNeedsProc(request)

        templateNeeds = {t.name:True for t in template.Need}
        needs_library = [t for t in needs if t.name not in templateNeeds]

        result.update({'template': template, 'needs':needs_library})
        return super(RoundHandler, self).pre_fill_values(request, result)


def show_latest_round(context, request):
    companyRound = GetRoundProc(request, {'token':request.matchdict['token']})
    return {'companyRound': companyRound}