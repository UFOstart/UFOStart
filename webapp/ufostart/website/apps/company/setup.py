from hnc.forms.handlers import FormHandler
from ufostart.lib.tools import group_by_n
from ufostart.website.apps.company.forms import RoundSetupForm
from ufostart.website.apps.models.company import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, SetCompanyTemplateProc, GetCompanyProc, GetAllNeedsProc, GetRoundProc


def basic(context, request):
    if context.user.Company.Template: request.fwd("website_company_setup_round")
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': group_by_n(templates)}


def set_template(context, request):
    templateName = request.matchdict['template']
    SetCompanyTemplateProc(request, {"token":context.user.Company.token,"Template":{"name":templateName}})
    context.user.Company = GetCompanyProc(request, {"token":context.user.Company.token})
    request.fwd("website_company_setup_round")



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
    company = GetRoundProc(request, {'token':context.user.Company.token})
    return {'latestRound': company.Round}