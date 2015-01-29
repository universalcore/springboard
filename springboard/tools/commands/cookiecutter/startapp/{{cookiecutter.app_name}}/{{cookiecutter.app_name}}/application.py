from ConfigParser import ConfigParser

from pyramid.config import Configurator

import pkg_resources


def main(global_config, **settings):

    cp = ConfigParser()
    cp.readfp(pkg_resources.resource_stream('springboard', 'defaults.ini'))
    defaults = dict(cp.items('springboard:pyramid'))
    defaults.update(settings)

    config = Configurator(settings=defaults)
    config.include('springboard.config')
    config.override_asset(
        to_override='springboard:templates/',
        override_with='{{cookiecutter.app_name}}:templates/')
    config.add_static_view(
        'static', '{{cookiecutter.app_name}}:static', cache_max_age=3600)

    return config.make_wsgi_app()
