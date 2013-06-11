from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, MultipleFormField, REQUIRED, StringField, RadioChoice, NullConfigModel, TextareaField
from hnc.forms.handlers import FormHandler
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import AddProductOfferProc, PledgeCompanyProc


class OfferChoiceField(RadioChoice):
    pass


def offer_choices(request):
    return request.root.company.Round.Product.Offers



class OffersField(MultipleFormField):
    template = 'ufostart:website/templates/company/controls/offer.html'
    add_more_link_label = 'Add Offer'
    fields = [
        StringField('name', "Offer", REQUIRED)
    ]


class ProductOfferForm(BaseForm):
    id="ProductOffer"
    label = ""
    fields=[
        OffersField("Offers")
    ]
    @classmethod
    def on_success(cls, request, values):
        round = request.root.company.Round
        values['token'] = round.Product.token
        AddProductOfferProc(request, {'Product': values})
        return {'success':True, 'redirect': request.rld_url()}


class ProductPledgeForm(BaseForm):
    id="ProductPledge"
    label = ""
    fields=[
        OfferChoiceField('offer', 'Your Offer', offer_choices, REQUIRED)
        , TextareaField('comment', 'Comment', REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        round = request.root.company.Round
        user = request.root.user

        values.update({'name': user.name, 'network':'ufo', 'networkId': user.token, 'picture':user.getPicture()})
        data = {'token': round.token, 'Pledge' : values}
        try:
            PledgeCompanyProc(request, data)
        except DBNotification, e:
            if e.message == 'AlreadyPledged':
                pass
            else:
                raise e

        return {'success':True, 'redirect': request.rld_url()}

class ProductOfferHandler(FormHandler):
    forms = [ProductOfferForm, ProductPledgeForm]

    def pre_fill_values(self, request, result):
        company = request.root.company
        result['company'] = company

        angelListId = company.angelListId if company.angelListId != 'asdfasdf' else ''
        angelListToken = company.angelListToken

        if angelListId:
            networkSettings = request.root['angellist']
            company = networkSettings.getCompanyData(angelListId, angelListToken)
            if company:
                roles = filter(lambda x: 'founder' in x.role, networkSettings.getCompanyRoles(angelListId, angelListToken))
                result.update({'al_company': company, 'company_roles': roles})
        return result



@require_login('ufostart:website/templates/auth/login.html')
def login(context, request):
    request.fwd("website_company_product", **context.urlArgs)


