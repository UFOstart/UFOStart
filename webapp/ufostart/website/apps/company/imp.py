# coding=utf-8
from hnc.forms.messages import GenericErrorMessage
from ufostart.website.apps.models.procs import SetCompanyAngelListPitchProc, CreateCompanyProc, CreateProductProc
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException


SESSION_FURL_TOKEN = 'ANGELLIST_FURL'
SESSION_SAVE_TOKEN = 'ANGELLIST_COMPANY_IMPORT'

def company_import_start(context, request):
    request.session[SESSION_FURL_TOKEN] = request.furl
    network = 'angellist'
    networkSettings = context[network]
    networkSettings.loginStart(request)

def company_import(context, request):
    network = 'angellist'
    networkSettings = context[network]
    try:
        profile = networkSettings.getProfile(request)
    except UserRejectedNotice, e:
        request.session.flash(GenericErrorMessage("You need to accept {} permissions to import your company profile.".format(network.title(), request.globals.project_name)), "generic_messages")
        request.fwd_raw(location = request.session.get('ANGELLIST_FURL', request.root.home_url))
    except SocialNetworkException, e:
        request.session.flash(GenericErrorMessage("{} authorization failed.".format(network.title())), "generic_messages")
        request.fwd_raw(location = request.session.get('ANGELLIST_FURL', request.root.home_url))
    else:
        if not profile:
            request.session.flash(GenericErrorMessage("{} authorization failed. It seems the request expired. Please try again".format(network.title())), "generic_messages")
            request.fwd_raw(location = request.session.get('ANGELLIST_FURL', request.root.home_url))
        else:
            request.fwd("website_company_import_list", network = network, user_id = profile['id'], token = profile['accessToken'])

def company_import_list(context, request):
    user_id = request.matchdict['user_id']
    token = request.matchdict['token']
    return {'companies':context['angellist'].getCompaniesData(user_id, token), 'back_url' : request.session.get('ANGELLIST_FURL', request.root.home_url)}

def company_import_confirm(context, request):
    company_id = request.matchdict['company_id']
    token = request.matchdict['token']
    al_company = context['angellist'].getCompanyData(company_id, token)
    al_company.token = token
    request.session[SESSION_SAVE_TOKEN] = al_company
    request.fwd_raw(location = request.session.pop('ANGELLIST_FURL', request.root.home_url))



