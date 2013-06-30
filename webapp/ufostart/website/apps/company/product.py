from operator import methodcaller
from hnc.apiclient import IntegerField
from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, MultipleFormField, REQUIRED, StringField, RadioChoice, NullConfigModel, TextareaField, HORIZONTAL_GRID, DecimalField, IntField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericErrorMessage
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.company.imp import SESSION_SAVE_TOKEN
from ufostart.website.apps.models.procs import SetProductOffersProc, PledgeCompanyProc, CreateProductProc
from ufostart.website.apps.forms.controls import FileUploadField, PictureGalleryUploadField, SanitizedHtmlField, CleanHtmlField


class ProductCreateForm(BaseForm):
    id="ProductCreate"
    label = ""
    fields=[
        StringField('name', "Name", REQUIRED)
        , SanitizedHtmlField("description", "Description", REQUIRED, input_classes='x-high')
        , PictureGalleryUploadField('Pictures', 'Drag multiple images into your gallery')
        , StringField("video", "Vimeo/YouTube")
    ]
    @classmethod
    def on_success(cls, request, values):
        if isinstance(values.get('pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]

        data = {'token': request.context.round.token, 'Product': values}
        result = CreateProductProc(request, data)
        return {'success':True, 'redirect': request.resource_url(request.context, 'product')}

class ProductCreateHandler(FormHandler):
    form = ProductCreateForm

    def __init__(self, context=None, request=None):
        if not context.canEdit:
            raise HTTPForbidden()
        super(ProductCreateHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            result['values'][self.form.id] = {
                'name': al_company.name
                , 'description': al_company.product_desc
                , 'picture': al_company.getFirstScreenShot()
                , 'video' : al_company.video_url
            }
        return super(ProductCreateHandler, self).pre_fill_values(request, result)





class ProductEditForm(ProductCreateForm):
    id="ProductEdit"
    @classmethod
    def on_success(cls, request, values):
        product = request.root.company.Round.Product
        values['token'] = product.token
        data = {'token': request.context.company.Round.token, 'Product': values}
        result = CreateProductProc(request, data)
        return {'success':True, 'redirect': request.resource_url(request.context)}


class ProductEditHandler(FormHandler):
    form = ProductEditForm

    def __init__(self, context=None, request=None):
        if not context.canEdit:
            raise HTTPForbidden()
        super(ProductEditHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        product = request.root.company.Round.Product
        result['values'][self.form.id] = product.unwrap()
        return super(ProductEditHandler, self).pre_fill_values(request, result)






class OfferChoiceField(RadioChoice):
    pass


def offer_choices(request):
    return request.root.company.Round.Product.Offers


class ProductOfferForm(BaseForm):
    id="ProductOffer"
    label = ""
    fields=[
        CleanHtmlField("name", "Title", REQUIRED)
        , SanitizedHtmlField("description", "Description", REQUIRED, input_classes='x-high')
        , DecimalField("price", "Price", REQUIRED)
        , IntField("stock", "Stock")
    ]
    @classmethod
    def on_success(cls, request, values):
        product = request.context.product
        offers = map(methodcaller("unwrap", sparse = True), product.Offers)
        offers.append(values)
        try:
            SetProductOffersProc(request, {'Product': {'token': product.token, 'Offers':offers}})
        except DBNotification, e:
            return {'errors': {'name': e.message}, 'success':False}
        return {'success':True, 'redirect': request.resource_url(request.context)}



def remove_offer(context, request):
    product = request.context.product
    offer_name = request.params.get("offer")
    if offer_name:
        offers = [o.unwrap(sparse = True) for o in product.Offers if o.name != offer_name]
        try:
            SetProductOffersProc(request, {'Product': {'token': product.token, 'Offers':offers}})
        except DBNotification, e:
            request.session.flash(GenericErrorMessage(e.message), "generic_messages")
            return {'success':False, 'redirect': request.resource_url(request.context)}
    raise HTTPFound(request.resource_url(request.context))





class ProductPledgeForm(BaseForm):
    id="ProductPledge"
    grid = HORIZONTAL_GRID
    label = ""
    fields=[
        OfferChoiceField('offer', 'Your Offer', offer_choices, REQUIRED, input_classes='radio')
        , TextareaField('comment', 'Comment')
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
    def __init__(self, context=None, request=None):
        if not context.company.product_is_setup:
            raise HTTPFound(request.resource_url(context.__parent__))
        super(ProductOfferHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        company = request.context.company
        result['company'] = company
        result['product'] = company.Round.Product
        return result



@require_login('ufostart:website/templates/auth/login.html')
def login(context, request):
    request.fwd("website_company_product", **context.urlArgs)


