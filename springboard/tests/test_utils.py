from unittest import TestCase

from springboard.utils import parse_repo_name


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
