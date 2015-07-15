from pyramid.security import forget, remember
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from unicore.hub.client import ClientException as HubClientException
from unicore.hub.client.utils import same_origin

from springboard.auth import USER_DATA_SESSION_KEY
from springboard.views.base import SpringboardViews


class AuthViews(SpringboardViews):

    @view_config(route_name='login')
    def login(self):
        hubclient = self.request.registry.hubclient
        response = HTTPFound()

        # redeem ticket to get user data
        ticket = self.request.GET.get('ticket', None)
        if ticket:
            try:
                user = hubclient.get_user(
                    ticket, self.request.route_url('redirect_to_login'))
                self.request.session[USER_DATA_SESSION_KEY] = user.data
                user_id = user.get('uuid')
                headers = remember(self.request, user_id)
                response.headerlist.extend(headers)

            except HubClientException:
                # TODO: show failed login notification to user
                pass

        redirect_url = self.request.GET.get('url', None)
        if not (redirect_url and same_origin(
                redirect_url, self.request.current_route_url())):
            redirect_url = self.request.route_url(route_name='home')
        response.location = redirect_url

        return response

    @view_config(route_name='redirect_to_login')
    def redirect_to_login(self):
        hubclient = self.request.registry.hubclient

        if self.request.referrer and same_origin(
                self.request.referrer, self.request.current_route_url()):
            callback_url = self.request.route_url(
                route_name='login', _query={'url': self.request.referrer})
        else:
            callback_url = self.request.route_url(route_name='login')

        return HTTPFound(hubclient.get_login_redirect_url(
            callback_url, locale=self.language))

    @view_config(route_name='logout')
    def logout(self):
        response = HTTPFound(headers=forget(self.request))

        if self.request.referrer and same_origin(
                self.request.referrer, self.request.current_route_url()):
            response.location = self.request.referrer
        else:
            response.location = self.request.route_url(route_name='home')

        return response
