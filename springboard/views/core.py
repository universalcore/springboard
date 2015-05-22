import os

from pyramid.view import view_config
from pyramid.view import notfound_view_config

from springboard.utils import ga_context
from springboard.views.base import SpringboardViews

from unicore.distribute.tasks import fastforward


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
        return {}
