from urlparse import parse_qsl, urlparse


def group_by_n(array, n=2):
    total = len(array)
    return [array[k*n:(k+1)*n] for k in range(total/n+1) if k*n<total]



def getYoutubeVideoId(url):
    scheme, netloc, url, params, query, fragment = urlparse(url)
    params = dict(parse_qsl(query))
    return params.get('v')

def getVimeoVideoId(vurl):
    scheme, netloc, url, params, query, fragment = urlparse(vurl)
    for e in url.split("/"):
        try:
            return int(e)
        except: pass
    return None