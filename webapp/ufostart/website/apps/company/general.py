from ufostart.website.apps.models.company import GetCompanyProc


def index(context, request):
    company = GetCompanyProc(request, {'token': context.user.Company.token})
    return {'company': company, 'hasRounds': len(company.Rounds) > 0}
