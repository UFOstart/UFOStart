from urlparse import urlparse, parse_qsl
from babel import dates
from hnc.tools.tools import word_truncate_by_letters
from httplib2 import Http
import simplejson

__author__ = 'Martin'

def html(text):
    return text.replace('\n', '<br/>')

def trunc(length):
    def f(text):
        if text is None: return ''
        return word_truncate_by_letters(text, length)
    return f

def nn(text, alt = ''):
    return alt if text is None else text

def coalesce(t1, t2):
    return t1 if t1 else t2 if t2 else ''


def format_date(date, format="short"):
    return dates.format_date(date, format, locale='en')

def getYoutubeVideoId(url):
    if not url: return None
    scheme, netloc, path, params, query, fragment = urlparse(url)
    params = dict(parse_qsl(query))
    return params.get('v')

def getVimeoVideoId(url):
    if not url: return None
    scheme, netloc, path, params, query, fragment = urlparse(url)
    for e in path.split("/"):
        try:
            return int(e)
        except: pass
    return None

def getSlideShareId(url):
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
            h = Http()
            resp, content = h.request("http://www.slideshare.net/api/oembed/2?url={}&format=json".format(url))
            result = simplejson.loads(content)
            return int(result['slideshow_id'])
        except: pass