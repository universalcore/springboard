from datetime import datetime

from pyramid import testing

from libthumbor import CryptoURL

from springboard.tests import SpringboardTestCase
from springboard.filters import (
    format_date_filter, thumbor_filter, markdown_filter,
    language_direction_filter, paginate_filter)


class TestFilters(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_format_date_filter_string(self):
        self.assertEqual(
            format_date_filter({}, '2012-12-31', '%d-%m-%y'),
            '31-12-12')

    def test_format_date_filter_date(self):
        self.assertEqual(
            format_date_filter({}, datetime(2012, 12, 31), '%d-%m-%y'),
            '31-12-12')

    def test_thumbor_filter(self):
        testing.setUp(settings={
            'thumbor.security_key': 'foo',
        })
        crypto = CryptoURL(key='foo')
        self.assertEqual(
            thumbor_filter({}, 'image', 25, 25),
            crypto.generate(width=25, height=25, image_url='image'))
        self.assertEqual(
            thumbor_filter({}, 'image', 25),
            crypto.generate(width=25, height=None, image_url='image'))

    def test_thumbor_filter_without_security_key(self):
        testing.setUp(settings={
            'thumbor.security_key': None,
        })
        self.assertEqual(
            thumbor_filter({}, 'image', 25, 25), '')
        self.assertEqual(
            thumbor_filter({}, 'image', 25), '')

    def test_markdown_filter(self):
        self.assertEqual(
            markdown_filter({}, '*foo*'),
            '<p><em>foo</em></p>')

    def test_markdown_filter_none(self):
        self.assertEqual(markdown_filter({}, None), None)
        self.assertEqual(markdown_filter({}, ''), '')

    def test_language_direction_filter(self):
        self.assertEqual(language_direction_filter('eng_GB'), 'ltr')
        self.assertEqual(language_direction_filter('urd_PK'), 'rtl')

    def test_paginate_filter(self):
        paginator = paginate_filter([1, 2, 3, 4, 5], 2,
                                    results_per_page=1,
                                    slider_value=2)
        self.assertEqual(paginator.get_page(), [3])
        self.assertEqual(paginator.page_numbers(), [1, 2, 3])
