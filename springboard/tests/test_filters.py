from datetime import datetime

from pyramid import testing

from jinja2 import Markup
from libthumbor import CryptoURL
from unicore.content.models import Category

from springboard.tests import SpringboardTestCase
from springboard.filters import (
    format_date_filter, thumbor_filter, markdown_filter,
    language_direction_filter, paginate_filter,
    get_category_title_filter, display_language_name_filter)


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
            crypto.generate(width=25, image_url='image'))
        self.assertEqual(
            thumbor_filter({}, 'image', 25, None),
            crypto.generate(width=25, height=0, image_url='image'))

    def test_thumbor_filter_without_security_key(self):
        testing.setUp(settings={
            'thumbor.security_key': None,
        })
        self.assertEqual(
            thumbor_filter({}, 'image', 25, 25), '')
        self.assertEqual(
            thumbor_filter({}, 'image', 25), '')

    def test_markdown_filter(self):
        result = markdown_filter({}, '*foo*')
        self.assertIsInstance(result, Markup)
        self.assertEqual(
            result,
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

    def test_get_category_title_filter(self):
        cat_test1 = Category({
            'title': 'Test Category 1', 'language': 'eng_GB'})
        cat_test2 = Category({
            'title': 'Test Category 2', 'language': 'eng_GB'})
        cat_array = [cat_test1, cat_test2]
        self.assertEqual(
            get_category_title_filter({}, cat_test1.uuid, cat_array),
            'Test Category 1')
        self.assertEqual(
            get_category_title_filter({}, cat_test2.uuid, cat_array),
            'Test Category 2')

    def test_display_language_name_filter(self):
        self.assertEqual(
            display_language_name_filter({}, 'eng_GB'), 'English')
        self.assertEqual(
            display_language_name_filter({}, 'swa_KE'), 'Kiswahili')
