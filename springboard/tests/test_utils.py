from unittest import TestCase

from springboard.utils import parse_repo_name, config_list, config_dict


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

    def tst_config_dict(self):
        self.assertEqual({
            'a': '1',
            'b': '2',
            'c': '3',
        }, 'a=1\nb=2\nc=3')
        self.assertEqual({
            'a': '1',
            'b': '2',
            'c': '3',
        }, 'a=1\nb=2\nc=3\n')
        self.assertEqual({}, '')
