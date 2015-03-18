from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import forget, remember
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid_beaker import set_cache_regions_from_settings

from unicore.hub.client import (User,
                                UserClient as HubUserClient,
                                ClientException as HubClientException)
from unicore.hub.client.utils import same_origin


USER_DATA_SESSION_KEY = 'user_data'


def includeme(config):
    config.add_route('login', '/login/')
    config.add_route('logout', '/logout/')
    config.add_route('redirect_to_login', '/login/hub/')
    config.scan('.auth')

    # set up sessions
    config.include('pyramid_beaker')
    set_cache_regions_from_settings(config.registry.settings)
    # set up unicore.hub client
    hubclient = HubUserClient.from_config(config.registry.settings)
    config.registry.hubclient = hubclient

    init_auth(config)


def init_auth(config):

    def user(request):
        if request.authenticated_userid:
            return User(
                request.registry.hubclient,
                request.session[USER_DATA_SESSION_KEY])

        return None

    def verify_user_in_session(user_id, request):
        user_data = request.session.get(USER_DATA_SESSION_KEY, None)

        if user_data is not None and user_data['uuid'] == user_id:
            return (user_id, )

        return None

    authn_policy = SessionAuthenticationPolicy(callback=verify_user_in_session)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_authentication_policy(authn_policy)
    config.add_request_method(user, reify=True)


class AuthViews(object):

    def __init__(self, request):
        self.request = request
        self.locale = request.locale_name

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
            callback_url, locale=self.locale))

    @view_config(route_name='logout')
    def logout(self):
        response = HTTPFound(headers=forget(self.request))

        if self.request.referrer and same_origin(
                self.request.referrer, self.request.current_route_url()):
            response.location = self.request.referrer
        else:
            response.location = self.request.route_url(route_name='home')

        return response
