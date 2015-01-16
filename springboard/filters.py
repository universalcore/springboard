from dateutil import parser

from jinja2 import contextfilter

from libthumbor import CryptoURL

from markdown import markdown

from pyramid.threadlocal import get_current_request


@contextfilter
def format_date_filter(ctx, date_string, format):
    dt = parser.parse(date_string)
    return dt.strftime(format)


@contextfilter
def thumbor_filter(ctx, image, width, height=None):
    request = get_current_request()
    security_key = request.registry.settings.get('thumbor.security_key')
    if not all([security_key, image]):
        return ''

    crypto = CryptoURL(key=security_key)
    return crypto.generate(width=width, height=height, image_url=image)


@contextfilter
def markdown_filter(ctx, content):
    return markdown(content)
