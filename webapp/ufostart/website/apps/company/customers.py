from hnc.apiclient.backend import DBNotification
from pyramid.renderers import render_to_response
from hnc.forms.messages import GenericErrorMessage, GenericSuccessMessage
from ufostart.website.apps.auth.social import get_social_profile
from ufostart.website.apps.models.procs import PledgeCompanyProc, SetCompanyAngelListPitchProc
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException


def company_import(context, request):
    network = 'angellist'
    networkSettings = context.settings.networks.get(network)
    slug = context.user.Company.slug
    try:
        profile = networkSettings.getProfile(request)
    except UserRejectedNotice, e:
        request.session.flash(GenericErrorMessage("You need to accept {} permissions to import your company profile.".format(network.title(), request.globals.project_name)), "generic_messages")
        request.fwd("website_company_customers", slug = slug)
    except SocialNetworkException, e:
        request.session.flash(GenericErrorMessage("{} authorization failed.".format(network.title())), "generic_messages")
        request.fwd("website_company_customers", slug = slug)
    else:
        if not profile:
            request.session.flash(GenericErrorMessage("{} authorization failed. It seems the request expired. Please try again".format(network.title())), "generic_messages")
            request.fwd("website_company_customers", slug = slug)
        else:
            request.fwd("website_company_import_list", network = network, user_id = profile['id'], token = profile['accessToken'], slug = slug)

def company_import_list(context, request):
    network = request.matchdict['network']
    user_id = request.matchdict['user_id']
    token = request.matchdict['token']
    networkSettings = context.settings.networks.get(network)
    return {'companies':networkSettings.getCompaniesData(user_id, token)}

def company_import_confirm(context, request):
    company_id = request.matchdict['company_id']
    token = request.matchdict['token']

    SetCompanyAngelListPitchProc(request, {'slug':request.matchdict['slug'], 'angelListId': company_id, 'angelListToken':token })
    request.fwd("website_company_customers", **context.urlArgs)



def index(context, request):
    company = context.company
    if not company.Round: request.fwd("website_company", **context.urlArgs)

    angelListId = company.angelListId if company.angelListId != 'asdfasdf' else ''
    angelListToken = company.angelListToken
    data = {'company': company}

    if angelListId:
        networkSettings = context.settings.networks.get('angellist')
        company = networkSettings.getCompanyData(angelListId, angelListToken)
        if company:
            roles = filter(lambda x: 'founder' in x.role, networkSettings.getCompanyRoles(angelListId, angelListToken))
            data.update({'company': company, 'company_roles': roles})
            template = "index.html"
        else:
            template = "index_empty.html"
    else:
        template = "index_empty.html"
    return render_to_response("ufostart:website/templates/company/customers/{}".format(template), data, request)





def pledge(request, company, values):

    data = {
        'token': company.Round.token
        , 'Pledge': values
    }
    try:
        PledgeCompanyProc(request, data)
    except DBNotification, e:
        if e.message == 'AlreadyPledged':
            pass
        else: raise e
    request.session.flash(GenericSuccessMessage("You have pledged successfully!"), "generic_messages")
    request.fwd("website_company_customers", slug = request.matchdict['slug'])


def pledge_decide(context, request):
    user = context.user
    if user.isAnon():
        return {}
    else:
        pledge(request, context.company, {'name': user.name, 'network':'ufo', 'networkId': user.token, 'picture':user.getPicture()})





def login_to_pledge(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    return networkSettings.loginStart(request
                , request.fwd_url('website_login_to_pledge_callback', network=network, slug = request.matchdict['slug'])
            )

def login_to_pledge_callback(context, request):
    network = request.matchdict['network']
    networkSettings = context.settings.networks.get(network)
    profile = get_social_profile(request, networkSettings
                    , request.fwd_url('website_login_to_pledge_callback', network=network, slug = request.matchdict['slug'])
                    , request.fwd_url("website_company_pledge_decide", slug = request.matchdict['slug'])
                )

    pledge(request, context.company, {'name': profile['name'], 'network':network, 'networkId': profile['id'], 'picture':profile['picture']})
