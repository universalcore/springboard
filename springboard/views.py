from pyramid.view import view_config
from pyramid.i18n import get_locale_name

from uc_helper import UCHelper


class SpringboardViews(object):

    def __init__(self, request):
        self.request = request
        self.language = get_locale_name(request)
        self.settings = request.registry.settings
        self.helper = UCHelper.from_git_url(
            self.settings['unicore.content_repo_url'], repos_dir='repos')

    def context(self, **context):
        defaults = {
            'language': self.language,
            'all_categories': self.helper.categories(),
            'all_pages': self.helper.pages(),
        }
        defaults.update(context)
        return defaults

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def index_view(self):
        return self.context()

    @view_config(route_name='category',
                 renderer='templates/category.jinja2')
    def category(self):
        uuid = self.request.matchdict['uuid']
        [category] = self.helper.categories().filter(uuid=uuid)
        return self.context(category=category)

    @view_config(route_name='page',
                 renderer='templates/page.jinja2')
    def page(self):
        uuid = self.request.matchdict['uuid']
        [page] = self.helper.pages().filter(uuid=uuid)
        [category] = self.helper.categories().filter(
            uuid=page.primary_category)
        return self.context(category=category,
                            page=page)
