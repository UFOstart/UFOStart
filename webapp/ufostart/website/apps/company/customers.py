from hnc.apiclient.backend import DBNotification
from pyramid.renderers import render_to_response
from hnc.forms.messages import GenericErrorMessage, GenericSuccessMessage
from ufostart.website.apps.models.procs import PledgeCompanyProc, SetCompanyAngelListPitchProc
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException







def index(context, request):
    company = context.company
    if not company.Round: request.fwd("website_company", **context.urlArgs)

    angelListId = company.angelListId if company.angelListId != 'asdfasdf' else ''
    angelListToken = company.angelListToken
    data = {'company': company}

    if angelListId:
        networkSettings = context['angellist']
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




def login(context, request, profile):
    pledge(request, context.company, {'name': profile.name, 'network':profile.network, 'networkId': profile.id, 'picture':profile.picture})

