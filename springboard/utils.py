from urlparse import urlparse


def parse_repo_name(repo_url):
    pr = urlparse(repo_url)
    _, _, repo_name_dot_git = pr.path.rpartition('/')
    if repo_name_dot_git.endswith('.git'):
        repo_name, _, _ = repo_name_dot_git.partition('.')
        return repo_name
    return repo_name_dot_git
