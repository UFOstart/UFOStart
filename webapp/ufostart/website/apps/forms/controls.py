from hnc.forms.formfields import NullConfigModel, StringField
from ufostart.models.tasks import TASK_CATEGORIES


def optionGetter(request):
    return [NullConfigModel()] + TASK_CATEGORIES


class FileUploadField(StringField):
    template = "ufostart:website/templates/company/controls/fileupload.html"
    group_classes='file-upload-control'



