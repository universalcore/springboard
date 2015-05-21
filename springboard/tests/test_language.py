from springboard.tests import SpringboardTestCase
from springboard.views import SpringboardViews

from pyramid import testing


class TestLanguages(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

        languages = ("[('eng_GB', 'English'), ('swa_KE', 'Swahili'),"
                     "('spa_ES', 'Spanish')]")
        featured_langs = "[('spa_ES', 'Spanish'), ('eng_GB', 'English')]"

        self.config = testing.setUp(settings={
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_url': self.workspace.working_dir,
            'available_languages': languages,
            'featured_languages': featured_langs
        })

    def tearDown(self):
        testing.tearDown()

    def test_locale_cookie(self):
        self.app = self.mk_app(self.workspace)
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

    def test_locales_displayed(self):
        view = SpringboardViews(self.mk_request())
        self.app = self.mk_app(self.workspace)
        langs = view.get_available_languages()
        self.assertEqual(
            langs, [('eng_GB', u'English'),
                    ('spa_ES', u'espa\xf1ol'), ('swa_KE', u'Kiswahili')])
        resp = self.app.get('/locale/change/')
        self.assertTrue(
            u'<a href="/locale/spa_ES/">espa\xf1ol</a>'
            in resp.body.decode('utf-8'))
        self.assertTrue(
            u'<a href="/locale/eng_GB/">English</a>'
            in resp.body.decode('utf-8'))
        self.assertTrue(
            u'<a href="/locale/swa_KE/">Kiswahili</a>'
            in resp.body.decode('utf-8'))
