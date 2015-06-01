import re
from functools import wraps
from urlparse import urlparse
import math

from elasticutils import S


def parse_repo_name(repo_url):
    pr = urlparse(repo_url)
    _, _, repo_name_dot_git = pr.path.rpartition('/')
    if repo_name_dot_git.endswith('.git'):
        repo_name, _, _ = repo_name_dot_git.partition('.')
        return repo_name
    return repo_name_dot_git


def ga_context(context_func):
    """
    A decorator for Cornice views that allows one to set extra parameters
    for Google Analytics tracking::

        @ga_context(lambda context: {'dt': context['category'].title, })
        @view_config(route_name='page')
        def view(request):
            return {
                'category': self.workspace.S(Category).filter(title='foo')[0],
            }

    :param func context_func:
        A function which takes one argument, a context dictionary made
        available to the template.
    :returns:
        A dict containing the extra variables for Google Analytics
        tracking.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            context = func(self, *args, **kwargs)
            self.request.google_analytics.update(context_func(context))
            return context
        return wrapper
    return decorator


def config_list(data):
    """
    A function that takes a string of values separated by newline characters
    and returns a list of those values

    :param func context_func:
        A function which takes one argument, a string of values separated by
        newline characters

    :returns:
        A list containing the values separated by newline characters,
        stripped of whitespace between the value and newline character

    """
    return filter(None, (x.strip() for x in data.splitlines()))


def config_dict(data):
    """
    A function that takes a string of pair values, indicated by '=', separated
    by newline characters and returns a dict of those value pairs

    :param func context_func:
        A function which takes one argument, a string of value pairs with
        '= between them' separated by newline characters

    :returns:
        A dict containing the value pairs separated by newline characters

    """
    lines = config_list(data)
    return dict(re.split('\s*=\s*', value) for value in lines)


class Paginator(object):
    """
    A thing that helps us page through result sets

    :param iterable results:
        The iterable of objects to paginate.
    :param int page:
        The page number, zero-based.
    :param int results_per_page:
        The number of objects in each page.
    :param int slider_value:
        The number of page numbers to display, excluding the current page.

    """

    def __init__(self, results, page, results_per_page=10, slider_value=5):
        self.results = results
        self.page = page
        self.results_per_page = results_per_page
        self.slider_value = slider_value
        self.buffer_value = self.slider_value / 2

    def total_count(self):
        if isinstance(self.results, S):
            return self.results.count()
        return len(self.results)

    def get_page(self):
        return self.results[self.page * self.results_per_page:
                            (self.page + 1) * self.results_per_page]

    def has_next_page(self):
        return ((self.page + 1) * self.results_per_page) < self.total_count()

    def has_previous_page(self):
        return self.page

    def total_pages(self):
        return int(
            math.ceil(
                float(self.total_count()) / float(self.results_per_page)))

    def page_numbers(self):
        if (self.page - self.buffer_value) < 0:
            return [page_number
                    for page_number in range(
                        0, min([self.slider_value, self.total_pages()]))]
        elif (self.page + self.buffer_value) >= self.total_pages():
            return [page_number
                    for page_number in range(
                        max((self.total_pages() - self.slider_value), 0),
                        self.total_pages())
                    ]
        else:
            return range(self.page - self.buffer_value,
                         self.page + self.buffer_value + 1)

    def page_numbers_left(self):
        page_numbers = self.page_numbers()
        if not any(page_numbers):
            return False
        return page_numbers[:page_numbers.index(self.page)]

    def page_numbers_right(self):
        page_numbers = self.page_numbers()
        if not any(page_numbers):
            return False
        return page_numbers[page_numbers.index(self.page) + 1:]

    def needs_start_ellipsis(self):
        page_numbers = self.page_numbers()
        if not any(page_numbers):
            return False
        return page_numbers[0] > 1

    def needs_end_ellipsis(self):
        page_numbers = self.page_numbers()
        if not any(page_numbers):
            return False
        return page_numbers[-1] < (self.total_pages() - 2)

    def show_start(self):
        page_numbers = self.page_numbers()
        if not any(page_numbers):
            return False
        return page_numbers[0] > 0

    def show_end(self):
        page_numbers = self.page_numbers()
        if not any(page_numbers):
            return False
        return page_numbers[-1] < self.total_pages() - 1
