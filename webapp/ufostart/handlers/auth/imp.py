# coding=utf-8
from hnc.forms.messages import GenericErrorMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.handlers.social import UserRejectedNotice, SocialNetworkException


SESSION_FURL_TOKEN = 'ANGELLIST_FURL'
SESSION_SAVE_TOKEN = 'ANGELLIST_COMPANY_IMPORT'


def getAngellist(request):
    settings = request.root.settings.networks['angellist']
    return settings.module(request.root, 'angellist', settings)

def company_import_start(context, request):
    request.session[SESSION_FURL_TOKEN] = request.furl
    context.loginStart(request)

def company_import(context, request):
    network = 'angellist'
    try:
        profile = context.getProfile(request)
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
            raise HTTPFound(request.resource_url(context, 'list', query=dict(network = network, user_id = profile['id'], token = profile['accessToken'])))

def company_import_list(context, request):
    user_id = request.params['user_id']
    token = request.params['token']
    return {'companies':context.getCompaniesData(user_id, token), 'back_url' : request.session.get('ANGELLIST_FURL', request.root.home_url)}

def company_import_confirm(context, request):
    company_id = request.params['company_id']
    token = request.params['token']
    al_company = context.getCompanyData(company_id, token)
    al_company.token = token
    request.session[SESSION_SAVE_TOKEN] = al_company
    request.fwd_raw(location = request.session.pop('ANGELLIST_FURL', request.root.home_url))



