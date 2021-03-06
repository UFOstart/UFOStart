import hashlib
import logging
import re
from urlparse import urlparse, parse_qsl
from xml.sax.saxutils import quoteattr
from BeautifulSoup import BeautifulSoup
from babel import dates
from httplib2 import Http
from HTMLParser import HTMLParser
import markdown
import simplejson
import smartypants
import unidecode

from hnc.apiclient import Mapping, TextField, IntegerField
from hnc.tools.tools import word_truncate_by_letters


log = logging.getLogger(__name__)

__author__ = 'Martin'

def json(data):
    return simplejson.dumps(data)


def attributes(data):
    if isinstance(data, basestring):
        return data
    elif isinstance(data, dict):
        return ' '.join(['{}={}'.format(k, quoteattr(v)) for k,v in data.items()])
    else:
        return ' '.join(['{}={}'.format(k, quoteattr(v)) for k,v in data])

def hash(txt):
    if not txt: return None
    return hashlib.md5(txt).hexdigest()

def html(text):
    if not text: return ''
    # catch any mis-typed en dashes
    converted_txt = text.replace(" - ", " -- ")
    converted_txt = smartypants.educateQuotes(converted_txt)
    converted_txt = smartypants.educateEllipses(converted_txt)
    converted_txt = smartypants.educateDashesOldSchool(converted_txt)
    # normalise line endings and insert blank line between paragraphs for Markdown
    converted_txt = re.sub("\r\n", "\n", converted_txt)
    converted_txt = re.sub("\n\n+", "\n", converted_txt)
    converted_txt = re.sub("\n", "\n\n", converted_txt)
    html = markdown.markdown(converted_txt)
    return html


def slugify(text):
    str = unidecode.unidecode(text).lower()
    return re.sub(r'\W+','.',str)

def trunc(length):
    def f(text):
        if text is None: return ''
        return word_truncate_by_letters(text, length)
    return f

def nn(text, alt = ''):
    return alt if text is None else text

def coalesce(t1, t2):
    return t1 if t1 else t2 if t2 else ''

def clean(txt):
  soup = BeautifulSoup(txt)
  for tag in soup.findAll(True):
      tag.extract()
  val = soup.renderContents()
  return val.decode("utf-8")


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def clean_coalesce(html1, txt2):
    result = ''
    if html1: result = strip_tags(html1).strip()
    return result or txt2



def make_link(txt):
    if not txt: return ''
    elif txt.startswith('http'):
        return txt
    else:
        return "http://{}".format(txt)



def format_date(date, format="short"):
    return dates.format_date(date, format, locale='en')

def format_datetime(date, format="full"):
    return dates.format_datetime(date, format, locale='en')

def getYoutubeVideoId(url):
    if not url or 'youtube' not in url.lower(): return None
    scheme, netloc, path, params, query, fragment = urlparse(url)
    params = dict(parse_qsl(query))
    return params.get('v')



def getYoutubeMeta(request, url):
    videoId =  getYoutubeVideoId(url)
    if not videoId: return None
    meta = request.globals.cache.get("YOUTUBE_{}".format(videoId))
    if not meta:
        try:
            log.info("YOUTUBE Cache miss for {}".format(url))
            h = Http()
            resp, data = h.request("https://gdata.youtube.com/feeds/api/videos/{}?v=2&alt=json".format(videoId))
            meta = simplejson.loads(data)
            request.globals.cache.set("YOUTUBE_{}".format(videoId), meta)
            return meta
        except: return None
    else:
        return meta

def getVimeoVideoId(url):
    if not url or 'vimeo' not in url.lower(): return None
    scheme, netloc, path, params, query, fragment = urlparse(url)
    for e in path.split("/"):
        try:
            return int(e)
        except: pass
    return None


class VimeoMeta(Mapping):
    id = IntegerField()
    user_id = IntegerField()
    thumbnail_small = TextField()
    thumbnail_medium = TextField()
    thumbnail_large = TextField()
    description = TextField()
    duration = TextField()
    mobile_url = TextField()
    title = TextField()
    user_name = TextField()


def getVimeoMeta(request, url):
    vimeoId =  getVimeoVideoId(url)
    if not vimeoId: return None
    meta = request.globals.cache.get("VIMEO_{}".format(vimeoId))
    if not meta:
        try:
            log.info("VIMEO Cache miss for {}".format(url))
            h = Http()
            resp, data = h.request("http://vimeo.com/api/v2/video/{}.json".format(vimeoId))
            meta = VimeoMeta.wrap(simplejson.loads(data)[0])
            request.globals.cache.set("VIMEO_{}".format(vimeoId), meta)
            return meta
        except: return None
    else:
        return meta




class SlideShareMeta(Mapping):
    id = IntegerField()
    slideshow_id = IntegerField()
    thumbnail = TextField()
    title = TextField()
    author_name = TextField()

def getSlideShareId(request, url):
    #http://www.slideshare.net/slideshow/embed_code/23145
    #http://www.slideshare.net/api/oembed/2?url=http://www.slideshare.net/mrcoryjim/presentation-roi-is-it-worth-it-yanceyu&format=jso
    if not url: return None
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if 'embed_code' in path.split('/'):
        try:
            return int(query.split('/')[-1])
        except: pass
    elif 'slideshare' in netloc:
        try:
            result = getSlideshareMeta(request, url)
            return result.slideshow_id
        except:
            return None


def getSlideshareMeta(request, url):
    if not url: return None
    meta = request.globals.cache.get("SLIDESHARE_{}".format(url))
    if not meta:
        try:
            log.info("Slideshare Cache miss for {}".format(url))
            h = Http()
            resp, content = h.request("http://www.slideshare.net/api/oembed/2?url={}&format=json".format(url))
            meta = SlideShareMeta.wrap(simplejson.loads(content))
            request.globals.cache.set("SLIDESHARE_{}".format(url), meta)
            return meta
        except: return None
    else:
        return meta
