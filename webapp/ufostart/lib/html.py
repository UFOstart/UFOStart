from hnc.tools.tools import word_truncate_by_letters
from markupsafe import Markup

__author__ = 'Martin'


def trunc(length):
    def f(text):
        if text is None: return ''
        return word_truncate_by_letters(text, length)
    return f

def nn(text, alt = ''):
    return alt if text is None else text

def coalesce(t1, t2):
    return t1 if t1 else t2 if t2 else ''

