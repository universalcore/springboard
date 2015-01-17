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
        print self.workspace.working_dir

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        request = testing.DummyRequest()
        views = SpringboardViews(request)
        context = views.index_view()
        print context['all_pages'].count()
