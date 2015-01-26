from springboard.tests import SpringboardTestCase
from springboard.views import SpringboardViews

from pyramid import testing


class TestViews(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.config = testing.setUp(settings={
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_url': self.workspace.working_dir,
        })

    def tearDown(self):
        testing.tearDown()

    def mk_request(self, params={}, matchdict={}, locale_name='eng_GB'):
        request = testing.DummyRequest(params)
        request.locale_name = locale_name
        request.matchdict = matchdict
        return request

    def test_default_context(self):
        views = SpringboardViews(self.mk_request())
        context = views.context()
        self.assertEqual(context['language'], 'eng_GB')
        self.assertEqual(context['all_categories'].count(), 0)
        self.assertEqual(context['all_pages'].count(), 0)

    def test_index_view(self):
        views = SpringboardViews(self.mk_request())
        context = views.index_view()
        self.assertEqual(set(context.keys()),
                         set(['language', 'all_categories', 'all_pages']))

    def test_category(self):
        [category] = self.mk_categories(self.workspace, count=1)
        views = SpringboardViews(
            self.mk_request(matchdict={'uuid': category.uuid}))
        context = views.category()
        self.assertEqual(context['category'].uuid, category.uuid)
        self.assertEqual(context['all_categories'].count(), 1)

    def test_page(self):
        [category] = self.mk_categories(self.workspace, count=1)
        [page] = self.mk_pages(self.workspace, count=1,
                               primary_category=category.uuid)
        views = SpringboardViews(
            self.mk_request(matchdict={'uuid': page.uuid}))
        context = views.page()
        self.assertEqual(context['category'].uuid, category.uuid)
        self.assertEqual(context['page'].uuid, page.uuid)
        self.assertEqual(context['all_categories'].count(), 1)
        self.assertEqual(context['all_pages'].count(), 1)

    def test_flatpage(self):
        [page] = self.mk_pages(self.workspace, count=1)
        views = SpringboardViews(
            self.mk_request(matchdict={'slug': page.slug}))
        context = views.flat_page()
        print context
