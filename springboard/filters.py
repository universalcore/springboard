from dateutil import parser

from jinja2 import contextfilter

from libthumbor import CryptoURL

from markdown import markdown

from pyramid.threadlocal import get_current_registry

from jinja2 import Markup
from babel import Locale, UnknownLocaleError
from pycountry import languages

from springboard.utils import Paginator
from unicore.languages import constants

# known right-to-left language codes
KNOWN_RTL_LANGUAGES = {"urd", "ara", "arc", "per", "heb", "kur", "yid"}


@contextfilter
def format_date_filter(ctx, timestamp, format):
    if isinstance(timestamp, basestring):
        timestamp = parser.parse(timestamp)
    return timestamp.strftime(format)


@contextfilter
def thumbor_filter(ctx, image, width, height=0):
    registry = get_current_registry(context=ctx)
    security_key = registry.settings.get('thumbor.security_key')
    if not all([security_key, image]):
        return ''

    # libthumbor generates an invalid url when height is None:
    # https://github.com/thumbor/libthumbor/blob/master/libthumbor/url.py#L19
    # Coerce it to 0. This scales the height proportionally.
    if height is None:
        height = 0

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
    try:
        term_code = languages.get(bibliographic=language_code).terminology
    except KeyError:
        term_code = language_code
    try:
        return Locale.parse(term_code).language_name
    except UnknownLocaleError:
        # Fallback value is the generated value in English or the code
        return constants.LANGUAGES.get(term_code, locale)


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
