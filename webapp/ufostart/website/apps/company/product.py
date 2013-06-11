
def index(context, request):
    company = context.company
    result = {'company': company}

    angelListId = company.angelListId if company.angelListId != 'asdfasdf' else ''
    angelListToken = company.angelListToken

    if angelListId:
        networkSettings = request.root['angellist']
        company = networkSettings.getCompanyData(angelListId, angelListToken)
        if company:
            roles = filter(lambda x: 'founder' in x.role, networkSettings.getCompanyRoles(angelListId, angelListToken))
            result.update({'al_company': company, 'company_roles': roles})

    return result