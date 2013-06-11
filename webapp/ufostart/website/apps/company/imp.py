from hnc.forms.messages import GenericErrorMessage
from ufostart.website.apps.models.procs import SetCompanyAngelListPitchProc
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException


def company_import_start(context, request):
    network = 'angellist'
    networkSettings = context[network]
    slug = context.user.Company.slug
    networkSettings.loginStart(request)

def company_import(context, request):
    network = 'angellist'
    networkSettings = context[network]
    slug = context.user.Company.slug
    try:
        profile = networkSettings.getProfile(request)
    except UserRejectedNotice, e:
        request.session.flash(GenericErrorMessage("You need to accept {} permissions to import your company profile.".format(network.title(), request.globals.project_name)), "generic_messages")
        request.fwd("website_company_company", slug = slug)
    except SocialNetworkException, e:
        request.session.flash(GenericErrorMessage("{} authorization failed.".format(network.title())), "generic_messages")
        request.fwd("website_company_company", slug = slug)
    else:
        if not profile:
            request.session.flash(GenericErrorMessage("{} authorization failed. It seems the request expired. Please try again".format(network.title())), "generic_messages")
            request.fwd("website_company_company", slug = slug)
        else:
            request.fwd("website_company_import_list", network = network, user_id = profile['id'], token = profile['accessToken'], slug = slug)

def company_import_list(context, request):
    network = 'angellist'
    user_id = request.matchdict['user_id']
    token = request.matchdict['token']
    networkSettings = context[network]
    return {'companies':networkSettings.getCompaniesData(user_id, token)}

def company_import_confirm(context, request):
    company_id = request.matchdict['company_id']
    token = request.matchdict['token']

    SetCompanyAngelListPitchProc(request, {'slug':request.matchdict['slug'], 'angelListId': company_id, 'angelListToken':token })
    request.fwd("website_company_company", **context.urlArgs)


