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
    config.add_translation_dirs('springboard:locale/')
    config.configure_celery(global_config['__file__'])

    return config.make_wsgi_app()
