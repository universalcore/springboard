import os

from elasticgit.search import SM

from springboard.utils import config_list, config_dict

from unicore.content.models import Category, Page, Localisation

from slugify import slugify


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
        repos = config_dict(self.settings['unicore.content_repos'])
        self.all_repo_paths = []
        self.all_index_prefixes = []
        for repo_name, index_prefix in repos.iteritems():
            self.all_repo_paths.append(os.path.join(repo_dir, repo_name))
            self.all_index_prefixes.append(index_prefix or slugify(repo_name))

        search_config = {
            'in_': self.all_repo_paths,
            'index_prefixes': self.all_index_prefixes
        }
        self.all_categories = SM(Category, **search_config).es(
            **self.es_settings)
        self.all_pages = SM(Page, **search_config).es(**self.es_settings)
        self.all_localisations = SM(Localisation, **search_config).es(
            **self.es_settings)
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
            'all_localisations': self.all_localisations,
            'all_categories': self.all_categories,
            'all_pages': self.all_pages,
        }
        defaults.update(context)
        return defaults
