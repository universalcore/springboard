import os

from pyramid.view import view_config
from pyramid.view import notfound_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from springboard.utils import ga_context, Paginator
from springboard.views.base import SpringboardViews

from unicore.distribute.tasks import fastforward


ONE_YEAR = 31536000


class CoreViews(SpringboardViews):

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

        empty_defaults = self.context(
            paginator=[],
            query=query,
            p=p,
        )

        # handle query exception
        if not query:
            return empty_defaults

        all_results = self.all_pages.query(
            content__query_string=query).filter(language=self.language)

        # no results found
        if all_results.count() == 0:
            return empty_defaults

        paginator = Paginator(all_results, p)

        # requested page number is out of range
        total_pages = paginator.total_pages()
        # sets the floor to 0
        p = p if p >= 0 else 0
        # sets the roof to `total_pages -1`
        p = p if p < total_pages else total_pages - 1
        paginator = Paginator(all_results, p)

        relevant_categories = self.all_categories.query().filter(
            language=self.language)

        return self.context(
            relevant_categories=relevant_categories,
            paginator=paginator,
            query=query,
            p=p,
        )

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
