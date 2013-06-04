from pyramid.renderers import render_to_response
from hnc.forms.messages import GenericErrorMessage, GenericSuccessMessage
from ufostart.website.apps.auth.social import get_social_profile
from ufostart.website.apps.models.procs import PledgeCompanyProc
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException


def company_import(context, request):
    network = 'angellist'
    networkSettings = context.settings.networks.get(network)
    try:
        profile = networkSettings.getProfile(request)
    except UserRejectedNotice, e:
        request.session.flash(GenericErrorMessage("You need to accept {} permissions to import your company profile.".format(network.title(), request.globals.project_name)), "generic_messages")
        request.fwd("website_company_customers", slug = request.matchdict['slug'])
    except SocialNetworkException, e:
        request.session.flash(GenericErrorMessage("{} authorization failed.".format(network.title())), "generic_messages")
        request.fwd("website_company_customers", slug = request.matchdict['slug'])
    else:
        if not profile:
            request.session.flash(GenericErrorMessage("{} authorization failed. It seems the request expired. Please try again".format(network.title())), "generic_messages")
            request.fwd("website_company_customers", slug = request.matchdict['slug'])
        else:
            request.fwd("website_company_import_list", network = network, user_id = profile['id'], token = profile['accessToken'], slug = request.matchdict['slug'])

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





def pledge(request, company, values):

    data = {
        'token': company.Round.token
        , 'Pledge': values
    }
    PledgeCompanyProc(request, data)
    request.session.flash(GenericSuccessMessage("You have pledged successfully!"), "generic_messages")
    request.fwd("website_company_customers", slug = request.matchdict['slug'])


def pledge_decide(context, request):
    user = context.user
    if user.isAnon():
        return {}
    else:
        pledge(request, context.company, {'name': user.name, 'network':'ufo', 'networkId': user.token, 'picture':user.picture})


def login_to_pledge(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    return networkSettings.loginStart(request, 'website_login_to_pledge_callback', redirect_kwargs = request.matchdict)

def login_to_pledge_callback(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    profile = get_social_profile(request, networkSettings, original_route = 'website_login_to_pledge_callback', redirect_kwargs = request.matchdict, error_route = "website_company_pledge_decide", error_kwargs = request.matchdict)

    pledge(request, context.company, {'name': profile['name'], 'network':network, 'networkId': profile['id'], 'picture':profile['picture']})
