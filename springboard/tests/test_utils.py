from unittest import TestCase

from mock import patch

from unicore.content.models import Category
from elasticgit.search import SM

from springboard.tests.base import SpringboardTestCase
from springboard.utils import (
    parse_repo_name, config_list, config_dict, Paginator)


class TestUtils(TestCase):

    def assertParsed(self, expected, dsn):
        return self.assertEqual(expected, parse_repo_name(dsn))

    def test_parse_repo_name(self):
        self.assertParsed('foo', 'git://domain/repo/foo.git')
        self.assertParsed('foo', 'git@domain:repo/foo.git')
        self.assertParsed('foo', 'ssh://git@domain:repo/foo.git')
        self.assertParsed('foo', 'http://domain/repo/foo.git')
        self.assertParsed('foo', 'https://domain/repo/foo.git')
        self.assertParsed('foo', 'git://domain/repo/foo')
        self.assertParsed('foo', 'ssh://git@domain:repo/foo')
        self.assertParsed('foo', 'http://domain/repo/foo')
        self.assertParsed('foo', 'https://domain/repo/foo')

    def test_config_list(self):
        self.assertEqual(['1', '2', '3'], config_list('1\n2\n3'))
        self.assertEqual(['1', '2', '3'], config_list('1\n2\n3\n'))
        self.assertEqual([], config_list(''))

    def test_config_dict(self):
        self.assertEqual({
            'a': '1',
            'b': '2',
            'c': '3',
        }, config_dict('a=1\nb=2\nc=3'))
        self.assertEqual({
            'foo': 'bar',
            'gum': 'tree',
            'elastic': 'search',
        }, config_dict('foo=bar\ngum=tree\nelastic=search\n'))
        self.assertEqual({}, config_dict(''))


class TestPaginator(TestCase):

    def mk_paginator(self, results, page, **kwargs):
        return Paginator(results, page, **kwargs)

    def test_first_page(self):
        paginator = self.mk_paginator(range(100), 0)
        self.assertTrue(paginator.has_next_page())
        self.assertFalse(paginator.has_previous_page())
        self.assertEqual(paginator.total_pages(), 10)
        self.assertEqual(paginator.page_numbers(), [0, 1, 2, 3, 4])
        self.assertFalse(paginator.needs_start_ellipsis())
        self.assertTrue(paginator.needs_end_ellipsis())
        self.assertEqual(paginator.page_numbers_left(), [])
        self.assertEqual(paginator.page_numbers_right(), [1, 2, 3, 4])

    def test_last_page(self):
        paginator = self.mk_paginator(range(100), 9)
        self.assertFalse(paginator.has_next_page())
        self.assertTrue(paginator.has_previous_page())
        self.assertEqual(paginator.total_pages(), 10)
        self.assertEqual(paginator.page_numbers(), [5, 6, 7, 8, 9])
        self.assertTrue(paginator.needs_start_ellipsis())
        self.assertFalse(paginator.needs_end_ellipsis())
        self.assertEqual(paginator.page_numbers_left(), [5, 6, 7, 8])
        self.assertEqual(paginator.page_numbers_right(), [])

    def test_middle_page(self):
        paginator = self.mk_paginator(range(100), 4)
        self.assertTrue(paginator.has_next_page())
        self.assertTrue(paginator.has_previous_page())
        self.assertEqual(paginator.total_pages(), 10)
        self.assertEqual(paginator.page_numbers(), [2, 3, 4, 5, 6])
        self.assertTrue(paginator.needs_start_ellipsis())
        self.assertTrue(paginator.needs_end_ellipsis())
        self.assertEqual(paginator.page_numbers_left(), [2, 3])
        self.assertEqual(paginator.page_numbers_right(), [5, 6])

    def test_show_start(self):
        paginator = self.mk_paginator(range(100), 3)
        self.assertTrue(paginator.show_start())
        self.assertFalse(paginator.needs_start_ellipsis())
        self.assertEqual(paginator.page_numbers_left(), [1, 2])
        self.assertEqual(paginator.page_numbers_right(), [4, 5])

    def test_show_end(self):
        paginator = self.mk_paginator(range(100), 7)
        self.assertTrue(paginator.show_start())
        self.assertTrue(paginator.needs_start_ellipsis())
        self.assertEqual(paginator.page_numbers(), [5, 6, 7, 8, 9])
        self.assertEqual(paginator.page_numbers_left(), [5, 6])
        self.assertEqual(paginator.page_numbers_right(), [8, 9])
        self.assertFalse(paginator.show_end())
        self.assertFalse(paginator.needs_end_ellipsis())

    def test_show_end_not_ellipsis(self):
        paginator = self.mk_paginator(range(100), 6)
        self.assertTrue(paginator.show_start())
        self.assertTrue(paginator.needs_start_ellipsis())
        self.assertEqual(paginator.page_numbers(), [4, 5, 6, 7, 8])
        self.assertEqual(paginator.page_numbers_left(), [4, 5])
        self.assertEqual(paginator.page_numbers_right(), [7, 8])
        self.assertTrue(paginator.show_end())
        self.assertFalse(paginator.needs_end_ellipsis())

    def test_small_result_set(self):
        paginator = self.mk_paginator(range(39), 0)
        self.assertFalse(paginator.show_start())
        self.assertFalse(paginator.needs_start_ellipsis())
        self.assertFalse(paginator.show_end())
        self.assertFalse(paginator.needs_end_ellipsis())
        self.assertEqual(paginator.page_numbers_left(), [])
        self.assertEqual(paginator.page_numbers_right(), [1, 2, 3])

    def test_large_end_result_set(self):
        paginator = self.mk_paginator(range(133), 12)
        self.assertEqual(paginator.page_numbers(), [9, 10, 11, 12, 13])
        self.assertEqual(paginator.page_numbers_left(), [9, 10, 11])
        self.assertEqual(paginator.page_numbers_right(), [13])
        self.assertFalse(paginator.show_end())
        self.assertFalse(paginator.needs_end_ellipsis())


class TestPaginatorWithESResults(TestPaginator, SpringboardTestCase):

    def mk_paginator(self, results, page, **kwargs):
        workspace = self.mk_workspace()
        patch_count = patch.object(
            SM, 'count', return_value=len(results))
        patch_count.start()
        self.addCleanup(patch_count.stop)
        results = SM(Category, in_=[workspace.working_dir])
        return Paginator(results, page, **kwargs)

    def test_get_page(self):
        paginator = self.mk_paginator(range(10), 0)
        page = paginator.get_page()
        self.assertIsInstance(page, SM)
