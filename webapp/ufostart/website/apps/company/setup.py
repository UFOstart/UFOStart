from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, REQUIRED, StringField, TextareaField
from hnc.forms.handlers import FormHandler
from pyramid.decorator import reify
from ufostart.website.apps.auth.social import require_login_cls
from ufostart.website.apps.company.imp import SESSION_SAVE_TOKEN
from ufostart.website.apps.models.procs import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, CreateCompanyProc
from ufostart.website.apps.forms.controls import FileUploadField, PictureGalleryUploadField


def basics(context, request):
    return {'templates': context.templates}

def details(context, request):
    return {'template': context.template}


class CompanyCreateForm(BaseForm):
    id="CompanyCreate"
    label = ""
    fields=[
        FileUploadField('logo', 'Project Logo', REQUIRED)
        , StringField('name', 'Project Name', REQUIRED)
        , TextareaField('pitch', 'Elevator Pitch', REQUIRED, max = 90)
        , TextareaField("description", "Description", REQUIRED, input_classes='x-high')
        , PictureGalleryUploadField('pictures', 'Drag multiple images into your gallery')
        , StringField("video", "Paste a Vimeo or Youtube Url")
        , StringField("slideshare", "Paste a Slideshare Url")
    ]

    @classmethod
    def on_success(cls, request, values):
        templateKey = request.context.__name__
        values['Template'] = {'key': templateKey}

        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            values['angelListId'] = al_company.id
            values['angelListToken'] = al_company.token

        try:
            company = CreateCompanyProc(request, {'token':request.root.user.token, 'Company':values})
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': "Already exists"}}
            else:
                return {'success':False, 'message': 'Something went wrong: {}'.format(e.message)}
        else:
            return {'success':True, 'redirect': request.root.company_url(request.root.user.getDefaultCompanySlug())}


class CreateProjectHandler(FormHandler):
    template = "ufostart:website/templates/company/setup/login.html"
    form = CompanyCreateForm

    def pre_fill_values(self, request, result):
        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            result['values'][self.form.id] = {'name': al_company.name, 'description': al_company.high_concept, 'logo': al_company.thumb_url}
        return super(CreateProjectHandler, self).pre_fill_values(request, result)
