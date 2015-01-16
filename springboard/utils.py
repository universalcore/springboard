from urlparse import urlparse


def parse_repo_name(repo_url):
    pr = urlparse(repo_url)
    _, _, repo_name_dot_git = pr.path.rpartition('/')
    repo_name, _, _ = repo_name_dot_git.partition('.')
    return repo_name
