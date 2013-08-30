from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import  REQUIRED, StringField, ChoiceField, HtmlAttrs
from hnc.forms.handlers import FormHandler
from ufostart.lib.baseviews import BaseForm
from ufostart.handlers.auth.imp import SESSION_SAVE_TOKEN
from ufostart.models.procs import CreateCompanyProc, EditCompanyProc
from ufostart.handlers.forms.controls import PictureUploadField, PictureGalleryUploadField, CleanHtmlField, SanitizedHtmlField, SlideshareField, VideoUrlField, UniqueNameField
from ufostart.models.tasks import NamedModel


def basics(context, request):
    return {'templates': context.templates}

def details(context, request):
    return {'template': context.template}


class CompanyCreateForm(BaseForm):
    id="CompanyCreate"
    label = ""
    fields=[
        PictureUploadField('logo', 'Logo', REQUIRED)
        , StringField('name', 'Name', REQUIRED)
        , UniqueNameField("slug", "UFOStart URL")
        , CleanHtmlField('pitch', 'Slogan', REQUIRED, max = 90)
        , SanitizedHtmlField("description", "Description", REQUIRED, input_classes='x-high')
        , PictureGalleryUploadField('Pictures', 'Drag multiple images into your gallery')
        , StringField("video", "Paste a Vimeo or Youtube Url")
        , StringField("slideShare", "Paste a Slideshare Url")
        , ChoiceField("currency", "Company Currency", optionGetter=lambda s: [NamedModel(name = 'EUR'), NamedModel(name = 'USD')])
    ]

    @classmethod
    def on_success(cls, request, values):
        templateKey = request.context.__name__
        if isinstance(values.get('pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]
        values['Template'] = {'key': templateKey}

        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            values['angelListId'] = al_company.id
            values['angelListToken'] = al_company.token
            del request.session[SESSION_SAVE_TOKEN]

        try:
            company = CreateCompanyProc(request, {'token':request.root.user.token, 'Company':values})
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': "Already exists"}}
            else:
                return {'success':False, 'message': 'Something went wrong: {}'.format(e.message)}
        else:
            return {'success':True, 'redirect': request.root.round_url(request.root.user.getDefaultCompanySlug(), '1')}


class CreateProjectHandler(FormHandler):
    form = CompanyCreateForm

    def pre_fill_values(self, request, result):
        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            result['values'][self.form.id] = {
                        'name': al_company.name
                        , 'pitch': al_company.high_concept
                        , 'description': al_company.product_desc
                        , 'logo': al_company.logo_url
                        , 'video': al_company.video_url
                        , 'Pictures': [{'url':unicode(scr)} for scr in al_company.screenshots]
                    }
        return super(CreateProjectHandler, self).pre_fill_values(request, result)



class CompanyEditForm(BaseForm):
    id="CompanyEdit"
    label = ""
    fields=[
        PictureUploadField('logo', 'Project Logo', REQUIRED)
        , StringField('name', 'Project Name', REQUIRED)
        , CleanHtmlField('pitch', 'Elevator Pitch', REQUIRED, max = 90)
        , SanitizedHtmlField("description", "Description", REQUIRED, input_classes='x-high')
        , PictureGalleryUploadField('Pictures', 'Drag multiple images into your gallery')
        , VideoUrlField("video", "Paste a Vimeo or Youtube Url")
        , SlideshareField("slideShare", "Paste a Slideshare Url")
    ]

    @classmethod
    def on_success(cls, request, values):
        company = request.context.company

        if isinstance(values.get('Pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]
        values['token'] = company.token

        try:
            company = EditCompanyProc(request, {'token':request.root.user.token, 'Company':values})
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': "Already exists"}}
            else:
                return {'success':False, 'message': 'Something went wrong: {}'.format(e.message)}
        else:
            return {'success':True, 'redirect': request.resource_url(request.context)}


class EditProjectHandler(FormHandler):
    form = CompanyEditForm

    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.company.unwrap(sparse = True)
        return super(EditProjectHandler, self).pre_fill_values(request, result)
