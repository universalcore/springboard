from springboard.tests import SpringboardTestCase

from pyramid import testing


class TestLanguages(SpringboardTestCase):

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

    def test_locale_cookie(self):
        [category_eng] = self.mk_categories(
            self.workspace, count=1, language='eng_GB',
            title='English Category')
        self.mk_pages(
            self.workspace, count=1, language='eng_GB',
            primary_category=category_eng.uuid)
        [category_spa] = self.mk_categories(
            self.workspace, count=1, language='spa_ES',
            title='Spanish Category')
        self.mk_pages(
            self.workspace, count=1, language='spa_ES',
            primary_category=category_spa.uuid)

        self.app.get('/locale/?language=eng_GB', status=302)
        resp = self.app.get('/', status=200)
        self.assertTrue('English Category' in resp.body)
        self.assertFalse('Spanish Category' in resp.body)

        self.app.get('/locale/?language=spa_ES', status=302)
        resp = self.app.get('/', status=200)
        self.assertTrue('Spanish Category' in resp.body)
        self.assertFalse('English Category' in resp.body)

    def test_change_locale_page(self):
        resp = self.app.get('/locale/change/')
        self.assertTrue(
            u'<a href="http://localhost/locale/spa_ES/">espa\xf1ol</a>'
            in resp.body.decode('utf-8'))
        self.assertTrue(
            u'<a href="http://localhost/locale/eng_GB/">English</a>'
            in resp.body.decode('utf-8'))
        self.assertTrue(
            u'<a href="http://localhost/locale/swa_KE/">Kiswahili</a>'
            in resp.body.decode('utf-8'))
