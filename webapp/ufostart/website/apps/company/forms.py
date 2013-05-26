from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm
from ufostart.website.apps.models.company import CreateRoundProc, SetCompanyTemplateProc, GetCompanyProc


class CompanyTemplateForm(BaseForm):
    fields = []

    @classmethod
    def on_success(cls, request, values):
        user = request.root.user
        templateName = values['template']
        SetCompanyTemplateProc(request, {"token":user.Company.token,"Template":{"name":templateName}})
        user.Company = GetCompanyProc(request, {"token":user.Company.token})
        return {'redirect': request.fwd_url("website_company_setup_round")}


class RoundSetupForm(BaseForm):
    fields = []

    @classmethod
    def on_success(cls, request, values):
        user = request.root.user
        needs = [values['needKey']] if isinstance(values['needKey'], basestring) else values['needKey']
        values = {"Company": { "token": user.Company.token, "Round": {"Needs": [{ "name": k } for k in needs]}}}
        try:
            round = CreateRoundProc(request, values)
        except DBNotification, e:
            raise e
        else:
            return {'success': True, 'redirect': request.fwd_url("website_company_round_view", token = round.token)}