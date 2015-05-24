import os
import tempfile
import pkg_resources
import yaml
import uuid

from ConfigParser import ConfigParser
from datetime import datetime
from unittest import TestCase

from webtest import TestApp
from pyramid import testing
from beaker.session import Session

from elasticgit import EG
from elasticgit.utils import load_class

from slugify import slugify

from unicore.content.models import Category, Page, Localisation

from springboard.application import main
from springboard.auth import USER_DATA_SESSION_KEY


class SpringboardTestCase(TestCase):

    destroy = 'KEEP_REPO' not in os.environ
    bootstrap_file = pkg_resources.resource_filename(
        'springboard', 'tests/test_springboard.yaml')
    working_dir = '.test_repos/'

    def mk_workspace(self, working_dir=None,
                     name=None,
                     url='http://localhost',
                     index_prefix=None,
                     auto_destroy=None,
                     author_name='Test Kees',
                     author_email='kees@example.org'):  # pragma: no cover
        name = name or self.id()
        working_dir = working_dir or self.working_dir
        index_prefix = index_prefix or slugify(name)
        auto_destroy = auto_destroy or self.destroy
        workspace = EG.workspace(os.path.join(working_dir, name), es={
            'urls': [url],
        }, index_prefix=index_prefix)
        if auto_destroy:
            self.addCleanup(workspace.destroy)

        workspace.setup(author_name, author_email)
        workspace
        while not workspace.index_ready():
            pass

        with open(self.bootstrap_file, 'r') as fp:
            bootstrap_data = yaml.safe_load(fp)
            for model, mapping in bootstrap_data['models'].items():
                workspace.setup_custom_mapping(load_class(model), mapping)

        return workspace

    def mk_app(self, workspace, ini_config={}, settings={}, main=main,
               extra_environ={}):  # pragma: no cover
        ini_defaults = {
            'celery': {
                'CELERY_ALWAYS_EAGER': True,
            }
        }
        ini_defaults.update(ini_config)

        settings_defaults = {
            'unicore.repos_dir': self.working_dir,
            'unicore.content_repo_urls': workspace.working_dir,
        }
        settings_defaults.update(settings)

        config_file = self.mk_configfile(ini_defaults)
        app = TestApp(main({
            '__file__': config_file,
            'here': os.path.dirname(workspace.working_dir),
        }, **settings_defaults), extra_environ=extra_environ)
        return app

    def mk_request(self, params={}, matchdict={}, locale_name='eng_GB'):
        request = testing.DummyRequest(params)
        request.locale_name = locale_name
        request.matchdict = matchdict
        request.google_analytics = {}
        request.user = None
        return request

    def mk_tempfile(self):  # pragma: no cover
        fp, pathname = tempfile.mkstemp(text=True)
        self.addCleanup(os.unlink, pathname)
        return os.fdopen(fp, 'w'), pathname

    def mk_configfile(self, data):  # pragma: no cover
        fp, pathname = self.mk_tempfile()
        with fp:
            cp = ConfigParser()
            # Do not lower case every key
            cp.optionxform = str
            for section, section_items in data.items():
                cp.add_section(section)
                for key, value in section_items.items():
                    cp.set(section, key, value)
            cp.write(fp)
        return pathname

    def mk_categories(
            self, workspace, count=2, language='eng_GB',
            **kwargs):   # pragma: no cover
        categories = []
        for i in range(count):
            data = {}
            data.update({
                'title': u'Test Category %s' % (i,),
                'language': language,
                'position': i
            })
            data.update(kwargs)
            data.update({
                'slug': slugify(data['title'])
            })

            category = Category(data)
            workspace.save(
                category, u'Added category %s.' % (i,))
            categories.append(category)

        workspace.refresh_index()
        return categories

    def mk_pages(
            self, workspace, count=2, timestamp_cb=None, language='eng_GB',
            **kwargs):  # pragma: no cover
        timestamp_cb = (
            timestamp_cb or (lambda i: datetime.utcnow().isoformat()))
        pages = []
        for i in range(count):
            data = {}
            data.update({
                'title': u'Test Page %s' % (i,),
                'content': u'this is sample content for pg %s' % (i,),
                'modified_at': timestamp_cb(i),
                'language': language,
                'position': i
            })
            data.update(kwargs)
            data.update({
                'slug': slugify(data['title'])
            })
            page = Page(data)
            workspace.save(page, message=u'Added page %s.' % (i,))
            pages.append(page)

        workspace.refresh_index()
        return pages

    def mk_localisation(self, workspace, locale='eng_GB',
                        **kwargs):  # pragma: no cover
        data = {'locale': locale}
        data.update(kwargs)
        localisation = Localisation(data)
        workspace.save(
            localisation, message=u'Added localisation %s.' % locale)
        workspace.refresh_index()
        return localisation

    def mk_session(self, logged_in=True, user_data={}):
        session_id = uuid.uuid4().hex
        session = Session(
            testing.DummyRequest(), id=session_id, use_cookies=False)

        if logged_in:
            user_data = user_data or {
                'uuid': uuid.uuid4().hex,
                'username': 'foo',
                'app_data': {'display_name': 'foobar'}
            }
            session[USER_DATA_SESSION_KEY] = user_data
            session['auth.userid'] = user_data['uuid']

        session.save()
        # return the session and cookie header
        return session, {'Cookie': 'beaker.session.id=%s' % session_id}
