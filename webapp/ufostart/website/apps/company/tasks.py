from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, TextareaField, REQUIRED
from hnc.forms.handlers import FormHandler
from ufostart.lib.tools import group_by_n
from ufostart.models.tasks import TASK_CATEGORIES
from ufostart.website.apps.models.procs import CreateCompanyProc, GetRoundProc, SetCompanyTemplateProc, GetCompanyProc, CreateRoundProc
from ufostart.website.apps.models.company import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, GetAllNeedsProc


class SetupCompanyForm(BaseForm):
    id="SetupCompany"
    label = ""
    fields=[
        StringField("name", "Name", REQUIRED)
        , TextareaField("description", "Description", input_classes="x-high")
    ]
    @classmethod
    def on_success(cls, request, values):
        data = {
                "token": request.root.user.token,
                "Company": values
            }
        try:
            company = CreateCompanyProc(request,  data)
        except DBNotification, e:
            raise e

        return {'success':True, 'redirect': request.fwd_url("website_company_invite")}

class SetupCompanyHandler(FormHandler):
    form = SetupCompanyForm




class TemplateForm(BaseForm):
    fields = []

    @classmethod
    def on_success(cls, request, values):
        user = request.root.user
        templateName = values['template']
        SetCompanyTemplateProc(request, {"token":user.Company.token,"Template":{"name":templateName}})
        user.Company = GetCompanyProc(request, {"token":user.Company.token})
        return {'redirect': request.fwd_url("website_company_setup_round")}

class TemplateHandler(FormHandler):
    form = TemplateForm

    def __init__(self, context=None, request=None):
        super(TemplateHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        templates = GetAllCompanyTemplatesProc(request)
        result['templates'] = group_by_n(templates)
        return super(TemplateHandler, self).pre_fill_values(request, result)





class NeedsForm(BaseForm):
    fields = []

    @classmethod
    def on_success(cls, request, values):
        user = request.root.user
        needs = [values['needKey']] if isinstance(values['needKey'], basestring) else values['needKey']
        values = {"Company": { "token": user.Company.token, "Round": {"Needs": [{ "name": k } for k in needs]}}}
        try:
            round = CreateRoundProc(request, values)
            if request.root.user and request.root.user.Company:
                request.root.user.Company.Rounds.append(round)
                request.session.save()
        except DBNotification, e:
            raise e
        else:
            return {'success': True, 'redirect': request.fwd_url("website_company_round_view", token = round.token)}

class NeedsHandler(FormHandler):
    form = NeedsForm
    def pre_fill_values(self, request, result):
        templateName = self.context.user.Company.Template.name
        template = GetTemplateDetailsProc(request, {'name': templateName})
        needs = GetAllNeedsProc(request)

        templateNeeds = {t.name:True for t in template.Need}
        needs_library = [t for t in needs if t.name not in templateNeeds]

        result.update({'template': template, 'needs':needs_library})
        return super(NeedsHandler, self).pre_fill_values(request, result)

    def getTaskCategories(self):
        return TASK_CATEGORIES



def show_latest_round(context, request):
    companyRound = GetRoundProc(request, {'token':request.matchdict['token']})
    return {'companyRound': companyRound}




def need_library(context, request):
        templates = GetAllCompanyTemplatesProc(request)
        templates = group_by_n(templates)
        return {'templates': templates}