from BeautifulSoup import BeautifulSoup
import formencode
from hnc.forms import formfields
from hnc.forms.formfields import StringField, TextareaField
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


class HTMLString(formencode.validators.String):
  messages = {"invalid_format":'There was some error in your HTML!'}
  valid_tags = ['a','strong', 'em', 'p', 'ul', 'ol', 'li', 'br', 'b', 'i', 'u', 's', 'strike', 'font', 'pre', 'blockquote', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
  valid_attrs = ['size', 'color', 'face', 'title', 'align', "style"]

  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              tag.extract()
          elif tag.name.lower() != "a":
              tag.attrs = [attr for attr in tag.attrs if attr[0].lower() in self.valid_attrs]
          else:
              attrs = dict(tag.attrs)
              tag.attrs = self.linkAttrs(attrs)
      val = soup.renderContents()
      return val.decode("utf-8")

class RemoveHtmlString(formencode.validators.String):
  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      result = ''
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              result+=tag.extract()
      return result


class SanitizedHtmlField(TextareaField):
    _validator = HTMLString

class CleanHtmlField(StringField):
    _validator = RemoveHtmlString