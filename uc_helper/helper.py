import os
from urlparse import urlparse

from elasticgit import EG

from unicore.content.models import Category, Page, Localisation


def parse_repo_name(repo_url):
    pr = urlparse(repo_url)
    _, _, repo_name_dot_git = pr.path.rpartition('/')
    repo_name, _, _ = repo_name_dot_git.partition('.')
    return repo_name


class UCHelper(object):

    @classmethod
    def from_git_url(cls, repo_url, repos_dir=''):
        repo_name = parse_repo_name(repo_url)
        return cls(os.path.join(repos_dir, repo_name), index_prefix=repo_name)

    def __init__(self, repo_path, index_prefix=None):
        self.workspace = EG.workspace(
            workdir=repo_path,
            index_prefix=index_prefix)

    def categories(self):
        return self.workspace.S(Category)

    def pages(self):
        return self.workspace.S(Page)

    def locales(self):
        return self.workspace.S(Localisation)
