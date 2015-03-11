import os

from elasticgit import EG

from pyramid.view import view_config

from springboard.utils import parse_repo_name, ga_context

from unicore.content.models import Category, Page
from unicore.distribute.tasks import fastforward

from slugify import slugify


class SpringboardViews(object):

    def __init__(self, request):
        self.request = request
        self.language = request.locale_name
        self.settings = request.registry.settings

        repo_name = parse_repo_name(self.settings['unicore.content_repo_url'])
        repo_path = os.path.join(
            self.settings.get('unicore.repos_dir', 'repos'), repo_name)
        index_prefix = slugify(repo_name)
        self.workspace = EG.workspace(
            repo_path, index_prefix=index_prefix)
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

    @view_config(route_name='home',
                 renderer='springboard:templates/home.jinja2')
    def index_view(self):
        return self.context()

    @ga_context(lambda context: {'dt': context['category'].title, })
    @view_config(route_name='category',
                 renderer='springboard:templates/category.jinja2')
    def category(self):
        uuid = self.request.matchdict['uuid']
        [category] = self.all_categories.filter(uuid=uuid)
        return self.context(category=category)

    @ga_context(lambda context: {'dt': context['page'].title, })
    @view_config(route_name='page',
                 renderer='springboard:templates/page.jinja2')
    def page(self):
        uuid = self.request.matchdict['uuid']
        [page] = self.all_pages.filter(uuid=uuid)
        [category] = self.all_categories.filter(
            uuid=page.primary_category)
        return self.context(category=category,
                            page=page)

    @view_config(route_name='flat_page',
                 renderer='springboard:templates/flat_page.jinja2')
    def flat_page(self):
        slug = self.request.matchdict['slug']
        [page] = self.all_pages.filter(language=self.language, slug=slug)
        return self.context(page=page)

    @view_config(route_name='api_notify', renderer='json')
    def api_notify(self):
        fastforward.delay(self.workspace.working_dir,
                          self.workspace.index_prefix)
        return {}
