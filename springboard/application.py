from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'springboard:static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('category', '/category/{uuid}/')
    config.add_route('page', '/page/{uuid}/')
    config.scan(".views")

    return config.make_wsgi_app()
