# coding=utf-8
from operator import methodcaller
from hnc.apiclient.backend import DBNotification, DBException
from hnc.forms.formfields import REQUIRED, StringField, TextareaField, HORIZONTAL_GRID, DecimalField, IntField, MultipleFormField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericErrorMessage
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from ufostart.lib.baseviews import BaseForm
from ufostart.models.procs import SetProductOffersProc, PledgeCompanyProc, CreateProductProc, RemoveProductOfferProc
from ufostart.apps.forms.controls import PictureGalleryUploadField, SanitizedHtmlField, CleanHtmlField, VideoUrlField, CurrencyIntField


class OfferField(MultipleFormField):
    template = 'ufostart:templates/common/controls/offers.html'
    fields = [
        CleanHtmlField("name", "Title", REQUIRED)
        , SanitizedHtmlField("description", "Description", REQUIRED, input_classes='x-high')
        , CurrencyIntField("price", "Price", REQUIRED, input_classes='data-input amount', maxlength=7, currency=u'€')
        , IntField("stock", "Stock", REQUIRED)
    ]


class ProductCreateForm(BaseForm):
    id="ProductCreate"
    label = ""
    fields=[
        StringField('name', "Name", REQUIRED)
        , SanitizedHtmlField("description", "Description", REQUIRED, input_classes='x-high')
        , OfferField("Offers", "Add Offers")
        , PictureGalleryUploadField('Pictures', 'Drag multiple images into your gallery')
        , VideoUrlField("video", "Vimeo/YouTube")
    ]
    @classmethod
    def on_success(cls, request, values):
        if isinstance(values.get('pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]

        offers = values.pop('Offers')
        data = {'token': request.context.round.token, 'Product': values}
        round = CreateProductProc(request, data)

        try:
            SetProductOffersProc(request, {'Product': {'token': round.Product.token, 'Offers':offers}})
        except DBNotification, e:
            return {'errors': {'name': e.message}, 'success':False}


        return {'success':True, 'redirect': request.resource_url(request.context)}

class ProductCreateHandler(FormHandler):
    form = ProductCreateForm





class ProductEditForm(ProductCreateForm):
    id="ProductEdit"
    @classmethod
    def on_success(cls, request, values):
        if isinstance(values.get('pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]

        product = request.context.product
        values['token'] = product.token
        data = {'token': request.context.round.token, 'Product': values}

        offers = values.pop('Offers')

        try:
            round = CreateProductProc(request, data)
            SetProductOffersProc(request, {'Product': {'token': product.token, 'Offers':offers}})
        except DBNotification, e:
            return {'errors': {'name': e.message}, 'success':False}


        return {'success':True, 'redirect': request.resource_url(request.context)}


class ProductEditHandler(FormHandler):
    form = ProductEditForm

    def __init__(self, context=None, request=None):
        if not context.canEdit:
            raise HTTPForbidden()
        super(ProductEditHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        product = request.context.product
        result['values'][self.form.id] = product.unwrap()
        return super(ProductEditHandler, self).pre_fill_values(request, result)


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
    offer_token = request.params.get("offer")
    if offer_token:
        try:
            RemoveProductOfferProc(request, {'token': offer_token})
        except (DBNotification, DBException), e:

            if request.is_xhr:
                return {'success':False, 'message': e.message}
            else:
                request.session.flash(GenericErrorMessage(e.message), "generic_messages")
                raise HTTPFound(request.resource_url(request.context))
        if request.is_xhr:
            return {'success':True, 'redirect': request.resource_url(request.context)}
        else:
            raise HTTPFound(request.resource_url(request.context))


class ProductPledgeForm(BaseForm):
    id="ProductPledge"
    grid = HORIZONTAL_GRID
    label = ""
    fields=[
        TextareaField('comment', 'Message')
    ]
    @classmethod
    def on_success(cls, request, values):
        round = request.context.round
        user = request.root.user

        offer_token = values['offer']
        comment = values[offer_token]

        pledge = {'name': user.name, 'network':'ufo', 'networkId': user.token, 'picture':user.getPicture(), 'comment': comment, 'offerToken': offer_token}
        data = {'token': round.token, 'Pledge' : pledge}
        try:
            PledgeCompanyProc(request, data)
        except DBNotification, e:
            if e.message == 'AlreadyPledged':
                pass
            else:
                raise e

        return {'success':True, 'redirect': request.resource_url(request.context)}

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
