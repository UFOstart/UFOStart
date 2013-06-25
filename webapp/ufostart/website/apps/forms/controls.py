from hnc.forms import formfields
from ufostart.models.tasks import TASK_CATEGORIES


def optionGetter(request):
    return [formfields.NullConfigModel()] + TASK_CATEGORIES


class FileUploadField(formfields.StringField):
    template = "ufostart:website/templates/company/controls/fileupload.html"
    group_classes='file-upload-control'



class TagSearchField(formfields.TagSearchField):
    template = "ufostart:website/templates/company/controls/tagsearch.html"
