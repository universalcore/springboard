import os

from elasticgit import EG

from pyramid.view import view_config
from pyramid.i18n import get_locale_name

from springboard.utils import parse_repo_name

from unicore.content.models import Category, Page


class SpringboardViews(object):

    def __init__(self, request):
        self.request = request
        self.language = get_locale_name(request)
        self.settings = request.registry.settings

        repo_name = parse_repo_name(self.settings['unicore.content_repo_url'])
        repo_path = os.path.join('repos', repo_name)
        self.workspace = EG.workspace(repo_path, index_prefix=repo_name)
        self.all_categories = self.workspace.S(Category)
        self.all_pages = self.workspace.S(Page)

    def context(self, **context):
        defaults = {
            'language': self.language,
            'all_categories': self.all_categories,
            'all_pages': self.all_pages,
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
        [category] = self.all_categories.filter(uuid=uuid)
        return self.context(category=category)

    @view_config(route_name='page',
                 renderer='templates/page.jinja2')
    def page(self):
        uuid = self.request.matchdict['uuid']
        [page] = self.all_pages.filter(uuid=uuid)
        [category] = self.all_categories.filter(
            uuid=page.primary_category)
        return self.context(category=category,
                            page=page)
