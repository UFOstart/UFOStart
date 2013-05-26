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
        # values = {"User": {"token": user.token, "Company": { "token": user.Company.token, "Round": {"Needs": [{ "name": k } for k in values['needKey']]}}}}
        values = {"Company": { "token": user.Company.token, "Round": {"Needs": [{ "name": k } for k in values['needKey']]}}}
        result = CreateRoundProc(request, values)
        return {'success': True, 'redirect': request.fwd_url("website_company_round_latest")}