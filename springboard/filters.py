from dateutil import parser

from jinja2 import contextfilter

from libthumbor import CryptoURL

from markdown import markdown

from pyramid.threadlocal import get_current_registry

from jinja2 import Markup
from babel import Locale
from pycountry import languages

from springboard.utils import Paginator


# known right-to-left language codes
KNOWN_RTL_LANGUAGES = {"urd", "ara", "arc", "per", "heb", "kur", "yid"}


@contextfilter
def format_date_filter(ctx, timestamp, format):
    if isinstance(timestamp, basestring):
        timestamp = parser.parse(timestamp)
    return timestamp.strftime(format)


@contextfilter
def thumbor_filter(ctx, image, width, height=None):
    registry = get_current_registry(context=ctx)
    security_key = registry.settings.get('thumbor.security_key')
    if not all([security_key, image]):
        return ''

    crypto = CryptoURL(key=security_key)
    return crypto.generate(width=width, height=height, image_url=image)


@contextfilter
def markdown_filter(ctx, content):
    if not content:
        return content
    return Markup(markdown(content))


@contextfilter
def display_language_name_filter(ctx, locale):
    language_code, _, country_code = locale.partition('_')
    term_code = languages.get(bibliographic=language_code).terminology
    return Locale.parse(term_code).language_name


def language_direction_filter(locale):
    language_code, _, country_code = locale.partition('_')
    if language_code in KNOWN_RTL_LANGUAGES:
        return 'rtl'
    return 'ltr'


def paginate_filter(results, page, results_per_page=10, slider_value=5):
    return Paginator(results, page, results_per_page, slider_value)


@contextfilter
def get_category_title_filter(ctx, primary_category_uuid, all_categories):
    for category in all_categories:
        if primary_category_uuid == category.uuid:
            return category.title
