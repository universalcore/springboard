from springboard.tests import SpringboardTestCase


from pyramid import testing
from unicore.content.models import Page


class TestSearch(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        settings = {
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repos': self.workspace.working_dir,
            'available_languages': '\n'.join([
                'eng_GB',
                'swa_KE',
                'spa_ES',
            ]),
            'featured_languages': '\n'.join([
                'spa_ES',
                'eng_GB',
            ])
        }
        self.config = testing.setUp(settings=settings)
        self.app = self.mk_app(self.workspace, settings=settings)

    def tearDown(self):
        testing.tearDown()

    def test_search_no_results(self):
        self.app = self.mk_app(self.workspace)

        resp = self.app.get('/search/', params={'q': ''}, status=200)
        self.assertTrue('No results found' in resp.body)

    def test_search_blank(self):
        self.app = self.mk_app(self.workspace)
        self.mk_pages(self.workspace)

        resp = self.app.get('/search/', params={'q': None}, status=200)
        self.assertTrue('No results found' in resp.body)

    def test_search_2_results(self):
        self.app = self.mk_app(self.workspace)
        self.mk_pages(self.workspace, count=2)
        resp = self.app.get('/search/', params={'q': 'sample'}, status=200)

        self.assertFalse('No results found' in resp.body)
        self.assertTrue('Test Page 0' in resp.body)
        self.assertTrue('Test Page 1' in resp.body)

    def test_search_multiple_results(self):
        self.app = self.mk_app(self.workspace)
        self.mk_pages(self.workspace, count=11)
        resp = self.app.get('/search/', params={'q': 'sample'}, status=200)
        self.assertTrue(
            'Next&nbsp;&gt;</a>'
            in resp.body)

    def test_search_profanity(self):
        self.app = self.mk_app(self.workspace)
        self.mk_pages(self.workspace, count=2)

        resp = self.app.get('/search/', params={'q': 'kak'}, status=200)

        self.assertTrue('No results found' in resp.body)

    def test_search_added_page(self):
        self.app = self.mk_app(self.workspace)
        mother_page = Page({
            'title': 'title for mother', 'language': 'eng_GB', 'position': 2,
            'content': 'Page for mother test page'})
        self.workspace.save(mother_page, 'Add mother page')

        self.workspace.refresh_index()

        resp = self.app.get('/search/', params={'q': 'mother'}, status=200)

        self.assertTrue('mother' in resp.body)
        self.assertFalse('No results found' in resp.body)

    def test_pagination(self):
        self.app = self.mk_app(self.workspace)
        self.mk_pages(self.workspace, count=15, content='baby')
        resp = self.app.get(
            '/search/', params={'q': 'baby', 'p': '0'}, status=200)
        self.assertFalse('Previous' in resp.body)
        self.assertTrue('Next' in resp.body)

    def test_search_language_filter(self):
        [category_eng] = self.mk_categories(
            self.workspace, count=1, language='eng_GB',
            title='English Category')
        self.mk_pages(
            self.workspace, count=1, language='eng_GB',
            primary_category=category_eng.uuid,
            content='Page for mother test page')
        [category_spa] = self.mk_categories(
            self.workspace, count=1, language='spa_ES',
            title='Spanish Category')
        self.mk_pages(
            self.workspace, count=1, language='spa_ES',
            primary_category=category_spa.uuid,
            content='Page for mother test page')

        self.app.get('/locale/?language=eng_GB', status=302)
        resp = self.app.get('/search/', params={'q': 'mother'}, status=200)
        self.assertTrue('English Category' in resp.body)
        self.assertFalse('Spanish Category' in resp.body)

        self.app.get('/locale/?language=spa_ES', status=302)
        resp = self.app.get('/search/', params={'q': 'mother'}, status=200)
        self.assertTrue('Spanish Category' in resp.body)
        self.assertFalse('English Category' in resp.body)
