from uuid import uuid4

from pyramid.events import NewResponse
from pyramid.events import subscriber

from unicore.google.tasks import pageview


ONE_YEAR = 31556952


@subscriber(NewResponse)
def new_request(event):
    request = event.request
    registry = request.registry
    response = event.response

    profile_id = registry.settings.get('ga.profile_id')
    if not profile_id:
        return

    client_id = request.cookies.get('ga_client_id', uuid4().hex)
    response.set_cookie('ga_client_id', value=client_id, max_age=ONE_YEAR)
    pageview.delay(profile_id, client_id, {
        'path': request.path,
        'uip': request.remote_addr,
        'dr': request.referer or '',
        'dh': request.domain,
        'user_agent': request.user_agent,
        'ul': request.accept_language,
    })
