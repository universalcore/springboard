import os

from elasticgit.search import SM

from pyramid.view import view_config
from pyramid.view import notfound_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from springboard.utils import (
    parse_repo_name, ga_context, config_list)

from unicore.content.models import Category, Page
from unicore.distribute.tasks import fastforward
from utils import EGPaginator

from slugify import slugify

ONE_YEAR = 31536000


class SpringboardViews(object):

    def __init__(self, request):
        self.request = request
        self.language = request.locale_name
        self.settings = request.registry.settings
        es_host = self.settings.get('es.host', 'http://localhost:9200')
        self.es_settings = {
            'urls': [es_host]
        }

        repo_dir = self.settings.get('unicore.repos_dir', 'repos')
        repo_names = map(
            lambda repo_url: parse_repo_name(repo_url),
            config_list(self.settings['unicore.content_repo_urls']))
        self.all_repo_paths = map(
            lambda repo_name: os.path.join(repo_dir, repo_name),
            repo_names)
        self.all_index_prefixes = map(
            lambda repo_name: slugify(repo_name),
            repo_names)

        search_config = {
            'in_': self.all_repo_paths,
            'index_prefixes': self.all_index_prefixes
        }
        self.all_categories = SM(Category, **search_config).es(
            **self.es_settings)
        self.all_pages = SM(Page, **search_config).es(**self.es_settings)
        self.available_languages = config_list(
            self.settings.get('available_languages', ''))
        self.featured_languages = config_list(
            self.settings.get('featured_languages', ''))
        self.display_languages = list(
            set(self.featured_languages) - set([self.language]))

    def context(self, **context):
        defaults = {
            'user': self.request.user,
            'available_languages': self.available_languages,
            'featured_languages': self.featured_languages,
            'display_languages': self.display_languages,
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

    @view_config(route_name='search',
                 renderer='springboard:templates/search_results.jinja2')
    def search(self):

        query = self.request.GET.get('q')
        p = int(self.request.GET.get('p', 0))

        empty_defaults = {
            'paginator': [],
            'query': query,
            'p': p,
        }

        # handle query exception
        if not query:
            return empty_defaults

        all_results = self.workspace.S(Page).query(
            content__query_string=query).filter(language=self.language)

        # no results found
        if all_results.count() == 0:
            return empty_defaults

        paginator = EGPaginator(all_results, p)

        # requested page number is out of range
        total_pages = paginator.total_pages()
        # sets the floor to 0
        p = p if p >= 0 else 0
        # sets the roof to `total_pages -1`
        p = p if p < total_pages else total_pages - 1
        paginator = EGPaginator(all_results, p)

        return {
            'paginator': paginator,
            'query': query,
            'p': p,
        }

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
        for working_dir, index_prefix in zip(self.all_repo_paths,
                                             self.all_index_prefixes):
            fastforward.delay(os.path.abspath(working_dir), index_prefix)
        return {}

    @notfound_view_config(renderer='springboard:templates/404.jinja2')
    def notfound(self):
        self.request.response.status = 404
        return self.context()

    @view_config(
        route_name='locale_change',
        renderer='springboard:templates/locale_change.jinja2')
    def locale_change(self):
        return self.context()

    @view_config(route_name='locale')
    @view_config(route_name='locale_matched')
    def set_locale_cookie(self):
        response = Response()
        language = self.request.matchdict.get('language') or \
            self.request.GET.get('language')

        if language:
            response.set_cookie('_LOCALE_', value=language, max_age=ONE_YEAR)

        return HTTPFound(location='/', headers=response.headers)
