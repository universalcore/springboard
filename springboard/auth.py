from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import set_cache_regions_from_settings

from unicore.hub.client import (User,
                                UserClient as HubUserClient)


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
