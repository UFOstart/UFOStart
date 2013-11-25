from hnc.apiclient import TextField, Mapping, BooleanField

__author__ = 'Martin'


class PageModel(Mapping):
    url = TextField()
    title = TextField()
    metaKeywords = TextField()
    metaDescription = TextField()
    content = TextField()
    active = BooleanField()
    linked = BooleanField()