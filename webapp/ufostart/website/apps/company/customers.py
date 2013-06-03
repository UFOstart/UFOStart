from operator import attrgetter
from pyramid.renderers import render_to_response
import simplejson
from hnc.forms.messages import GenericErrorMessage, GenericSuccessMessage
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException


def company_import(context, request):
    network = 'angellist'
    networkSettings = context.settings.networks.get(network)
    try:
        profile = networkSettings.getProfile(request)
    except UserRejectedNotice, e:
        request.session.flash(GenericErrorMessage("You need to accept {} permissions to import your company profile.".format(network.title(), request.globals.project_name)), "generic_messages")
        request.fwd("website_company_customers")
    except SocialNetworkException, e:
        request.session.flash(GenericErrorMessage("{} authorization failed.".format(network.title())), "generic_messages")
        request.fwd("website_company_customers")
    else:
        if not profile:
            request.session.flash(GenericErrorMessage("{} authorization failed. It seems the request expired. Please try again".format(network.title())), "generic_messages")
            request.fwd("website_company_customers")
        else:
            request.fwd("website_company_import_list", network = network, user_id = profile['id'], token = profile['accessToken'])

def company_import_list(context, request):
    network = request.matchdict['network']
    user_id = request.matchdict['user_id']
    token = request.matchdict['token']
    networkSettings = context.settings.networks.get(network)
    return {'companies':networkSettings.getCompaniesData(user_id, token)}

def company_import_confirm(context, request):
    network = request.matchdict['network']
    company_id = request.matchdict['company_id']
    token = request.matchdict['token']
    networkSettings = context.settings.networks.get(network)
    company = networkSettings.getCompanyData(company_id, token)
    roles = filter(lambda x: 'founder' in x.role, networkSettings.getCompanyRoles(company_id, token))
    return {'company': company, 'company_roles': roles}


def index(context, request):
    company = None
    if company:
        template = "index.html"
    else:
        template = "index_empty.html"
    return render_to_response("ufostart:website/templates/company/customers/{}".format(template), {'company':company}, request)



def pledge_decide(context, request):
    if request.user.isAnon():
        return {}
    else:
        request.session.flash(GenericSuccessMessage("You have pledged successfully!"), "generic_messages")
        request.fwd("website_company_customers")

