from pyramid.view import view_config


class SpringboardViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='templates/mytemplate.pt')
    def index_view(self):
        return {'project': 'springboard'}
