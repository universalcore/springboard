from ConfigParser import ConfigParser

from pyramid.config import Configurator

import pkg_resources


def main(global_config, **settings):

    cp = ConfigParser()
    cp.readfp(pkg_resources.resource_stream('springboard', 'defaults.ini'))
    defaults = dict(cp.items('springboard:pyramid'))
    defaults.update(settings)

    config = Configurator(settings=defaults)
    config.add_static_view('static', 'springboard:static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('category', '/category/{uuid}/')
    config.add_route('page', '/page/{uuid}/')
    config.scan(".views")

    return config.make_wsgi_app()
