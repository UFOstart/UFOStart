from ufostart.lib.tools import group_by_n
from ufostart.website.apps.models.company import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, SetCompanyTemplateProc, GetCompanyProc, GetAllNeedsProc


def basic(context, request):
    if context.user.Company.Template: request.fwd("website_company_setup_round")
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': group_by_n(templates)}


def set_template(context, request):
    templateName = request.matchdict['template']
    SetCompanyTemplateProc(request, {"token":context.user.Company.token,"Template":{"name":templateName}})
    context.user.Company = GetCompanyProc(request, {"token":context.user.Company.token})
    request.fwd("website_company_setup_round")

def round(context, request):
    templateName = context.user.Company.Template.name
    template = GetTemplateDetailsProc(request, {'name': templateName})
    needs = GetAllNeedsProc(request)
    return {'template': template, 'needs':needs}


