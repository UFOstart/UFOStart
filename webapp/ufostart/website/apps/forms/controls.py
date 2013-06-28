import formencode
from hnc.forms import formfields
from ufostart.models.tasks import TASK_CATEGORIES


def optionGetter(request):
    return [formfields.NullConfigModel()] + TASK_CATEGORIES


class FileUploadField(formfields.StringField):
    template = "ufostart:website/templates/company/controls/fileupload.html"
    group_classes='file-upload-control'

    def getInputAttrs(self, request):
        attrs = self.attrs.getInputAttrs(request)
        if self.min:
            attrs += ' minlength="{}"'.format(self.min)
        if self.max:
            attrs += ' maxlength="{}"'.format(self.max)
        return attrs

class PictureGalleryUploadField(formfields.StringField):
    template = "ufostart:website/templates/company/controls/multifileupload.html"
    group_classes='multi-file-upload-control'
    def getValidator(self, request):
        return {self.name: formencode.ForEach(url = formencode.validators.String(required=True))}



class TagSearchField(formfields.TagSearchField):
    template = "ufostart:website/templates/company/controls/tagsearch.html"
