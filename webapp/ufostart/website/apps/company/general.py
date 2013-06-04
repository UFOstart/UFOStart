from ufostart.website.apps.models.procs import GetCompanyProc


def index(context, request):
    company = GetCompanyProc(request, {'token': context.user.Company.token})
    return {'company': company, 'currentRound':company.Round}
