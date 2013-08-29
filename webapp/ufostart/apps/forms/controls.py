from BeautifulSoup import BeautifulSoup
import formencode
from hnc.forms import formfields
from hnc.forms.formfields import StringField, TextareaField, IntField
from ufostart.lib.html import getSlideshareMeta, getVimeoMeta, getYoutubeMeta


_ = lambda s:s

class CurrencyIntField(IntField):
    template = "ufostart:templates/company/controls/currencyint.html"


class PictureUploadField(formfields.StringField):
    template = "ufostart:templates/company/controls/pictureupload.html"
    group_classes='file-upload-control'

    def getInputAttrs(self, request):
        attrs = self.attrs.getInputAttrs(request)
        if self.min:
            attrs += ' minlength="{}"'.format(self.min)
        if self.max:
            attrs += ' maxlength="{}"'.format(self.max)
        return attrs

class FileUploadField(PictureUploadField):
    template = "ufostart:templates/company/controls/fileupload.html"

class PictureGalleryUploadField(formfields.StringField):
    template = "ufostart:templates/company/controls/multifileupload.html"
    group_classes='multi-file-upload-control'
    def getValidator(self, request):
        return {self.name: formencode.ForEach(url = formencode.validators.String(required=True))}



class TagSearchField(formfields.TagSearchField):
    template = "ufostart:templates/company/controls/tagsearch.html"


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





class SlideShareUrl(formencode.validators.String):
    messages = dict(
        tooLong=_('Enter a value not more than %(max)i characters long'),
        tooShort=_('Enter a value %(min)i characters long or more'),
        notSlideshareUrl = _("Please add a valid slideshare url. You can find it in the sharing options of the presentation.")
    )
    def _to_python(self, value, state):
        result = super(SlideShareUrl, self)._to_python(value, state)

        if not getSlideshareMeta(state, value):
            raise formencode.api.Invalid(
                self.message('notSlideshareUrl', state, max=self.max), value, state)
        else: return result

class SlideshareField(StringField):
    _validator = SlideShareUrl



class VideoUrl(formencode.validators.String):
    messages = dict(
        tooLong=_('Enter a value not more than %(max)i characters long'),
        tooShort=_('Enter a value %(min)i characters long or more'),
        notVideoUrl = _("Please add a valid youtube or vimeo url. You can find it in the browser address bar when watching the video.")
    )
    def _to_python(self, value, state):
        result = super(VideoUrl, self)._to_python(value, state)

        if not getYoutubeMeta(state, value) and not getVimeoMeta(state, value):
            raise formencode.api.Invalid(
                self.message('notVideoUrl', state, max=self.max), value, state)
        else: return result

class VideoUrlField(StringField):
    _validator = VideoUrl