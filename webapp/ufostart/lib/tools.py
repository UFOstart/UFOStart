from decimal import Decimal
from urlparse import parse_qsl, urlparse
from babel.numbers import get_currency_symbol, format_currency as fc, format_decimal as fdec


def group_by_n(array, n=2):
    total = len(array)
    return [array[k*n:(k+1)*n] for k in range(total/n+1) if k*n<total]




def format_int_amount(number, locale = 'en'):
    if number is None:
        return ''
    fnumber = Decimal('%.2f' % number)
    return fdec(fnumber, format='#,##0', locale=locale)


def format_currency(number, currency = 'USD', locale = 'en'):
    if round(number) == number:
        return u'{}{}'.format(get_currency_symbol(currency, locale = locale), format_int_amount(number, locale))
    else:
        fnumber = Decimal('%.2f' % number)
        return fc(fnumber, currency, locale = locale)
