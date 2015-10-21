import mock

from datetime import datetime

from springboard.tests import SpringboardTestCase
from springboard.views.core import CoreViews
from springboard.utils import parse_repo_name

from pyramid import testing


class TestViews(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.settings = {
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_urls': self.workspace.working_dir,
        }
        self.config = testing.setUp(settings=self.settings)

    def tearDown(self):
        testing.tearDown()

    def test_default_context(self):
        views = CoreViews(self.mk_request())
        context = views.context()
        self.assertEqual(context['language'], 'eng_GB')
        self.assertEqual(context['all_categories'].count(), 0)
        self.assertEqual(context['all_pages'].count(), 0)

    def test_index_view(self):
        views = CoreViews(self.mk_request())
        context = views.index_view()
        self.assertEqual(set(context.keys()),
                         set(['user', 'language', 'all_categories',
                              'all_pages', 'featured_languages',
                              'available_languages', 'display_languages',
                              'all_localisations']))

    def test_health(self):
        app = self.mk_app(self.workspace, settings=self.settings)
        app.get('/health/', status=200)

    def test_category(self):
        [category] = self.mk_categories(self.workspace, count=1)
        views = CoreViews(
            self.mk_request(matchdict={'uuid': category.uuid}))
        context = views.category()
        self.assertEqual(context['category'].uuid, category.uuid)
        self.assertEqual(context['all_categories'].count(), 1)

    def test_page(self):
        [category] = self.mk_categories(self.workspace, count=1)
        [page] = self.mk_pages(self.workspace, count=1,
                               primary_category=category.uuid)
        views = CoreViews(
            self.mk_request(matchdict={'uuid': page.uuid}))
        context = views.page()
        self.assertEqual(context['category'].uuid, category.uuid)
        self.assertEqual(context['page'].uuid, page.uuid)
        self.assertEqual(context['all_categories'].count(), 1)
        self.assertEqual(context['all_pages'].count(), 1)

    def test_page_with_no_category(self):
        [page] = self.mk_pages(self.workspace, count=1)
        views = CoreViews(
            self.mk_request(matchdict={'uuid': page.uuid}))
        context = views.page()
        self.assertEqual(context['page'].uuid, page.uuid)
        self.assertEqual(context['all_categories'].count(), 0)
        self.assertEqual(context['all_pages'].count(), 1)

    def test_flatpage(self):
        [page] = self.mk_pages(self.workspace, count=1)
        views = CoreViews(
            self.mk_request(matchdict={'slug': page.slug}))
        context = views.flat_page()
        self.assertEqual(context['page'].uuid, page.uuid)

    def test_404_page(self):
        self.app = self.mk_app(self.workspace)
        resp = self.app.get('/blahblah', expect_errors=True)
        self.assertIn('<h1>404 not found</h1>', resp.body)
        self.assertEqual(resp.status_int, 404)

    @mock.patch('springboard.tasks.pull.delay')
    def test_api_notify(self, mock_delay):
        request = self.mk_request()
        request.method = 'POST'

        views = CoreViews(request)
        response = views.api_notify()
        self.assertEqual(mock_delay.call_count, 1)
        args, kwargs = mock_delay.call_args
        self.assertEqual(response, {})
        self.assertEqual(kwargs['repo_url'], self.workspace.working_dir)
        self.assertEqual(kwargs['index_prefix'], self.workspace.index_prefix)
        self.assertEqual(kwargs['es'], views.es_settings)

    def test_multiple_repos(self):
        workspace1 = self.workspace
        workspace2 = self.mk_workspace(name='test_multiple_repos-2')
        testing.setUp(settings={
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_urls': '\n%s\n%s' % (workspace1.working_dir,
                                                       workspace2.working_dir),
        })
        views = CoreViews(self.mk_request())
        indexes = map(
            lambda path: '%s-master' % parse_repo_name(path),
            [workspace1.working_dir, workspace2.working_dir])
        self.assertEqual(indexes, views.all_pages.get_indexes())
        self.assertEqual(indexes, views.all_categories.get_indexes())

    @mock.patch('unicore.google.tasks.pageview.delay')
    def test_ga_page_titles(self, mock_task):
        self.workspace = self.mk_workspace(name='ffl')
        [category] = self.mk_categories(self.workspace, count=1, position=1)
        [page] = self.mk_pages(
            self.workspace, count=1, position=1,
            created_at=datetime.utcnow().isoformat(),
            primary_category=category.uuid)

        app = self.mk_app(self.workspace, settings={'ga.profile_id': 'ID-000'})

        app.get('/')
        data = mock_task.call_args[0][2]
        self.assertEqual(data['dt'], 'Home')

        app.get('/category/%s/' % category.uuid)
        data = mock_task.call_args[0][2]
        self.assertEqual(data['dt'], category.title)

        app.get('/page/%s/' % page.uuid)
        data = mock_task.call_args[0][2]
        self.assertEqual(data['dt'], page.title)

        app.get('/locale/change/')
        data = mock_task.call_args[0][2]
        self.assertEqual(data['dt'], 'Choose Language')

        app.get('/locale/eng_GB/')
        data = mock_task.call_args[0][2]
        self.assertEqual(data['dt'], 'Set Language')

        app.get('/locale/?locale=eng_GB')
        data = mock_task.call_args[0][2]
        self.assertEqual(data['dt'], 'Set Language')
