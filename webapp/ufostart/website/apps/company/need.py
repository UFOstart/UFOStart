from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import NullConfigModel, BaseForm, StringField, REQUIRED, TextareaField, ChoiceField, TypeAheadField, TagSearchField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from ufostart.models.tasks import TASK_CATEGORIES
from ufostart.website.apps.models.procs import CreateNeedProc



def index(context, request):
    return {}

def optionGetter(request):
    return [NullConfigModel()] + TASK_CATEGORIES







class NeedCreateForm(BaseForm):
    id="NeedCreate"
    label = ""
    fields=[
        StringField('name', "Need Name", REQUIRED)
        , TextareaField("description", "Description", REQUIRED)
        , ChoiceField("category", "Need Type", optionGetter, REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        try:
            CreateNeedProc(request, values)
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This need already exists, if you intend to create this need, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_expert_dashboard")}

class NeedCreateHandler(FormHandler):
    form = NeedCreateForm



class FileUploadField(StringField):
    template = "ufostart:website/templates/company/controls/fileupload.html"


class NeedEditForm(BaseForm):
    id="NeedEdit"
    label = ""
    fields = [
        FileUploadField("picture", 'Picture', group_classes='file-upload-control')
        , TextareaField("description", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("tags", "Related Tags", '/web/tag/search', 'TagSearchResult', attrs = REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            CreateNeedProc(request, values)
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This need already exists, if you intend to Edit this need, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need edited successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_expert_dashboard")}

class NeedEditHandler(FormHandler):
    form = NeedEditForm

    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = self.context.need.unwrap()
        return super(NeedEditHandler, self).pre_fill_values(request, result)
