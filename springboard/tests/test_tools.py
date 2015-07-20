import os
import shutil
import responses
from ConfigParser import ConfigParser
from StringIO import StringIO

import yaml

from mock import patch, Mock

from springboard.tests import SpringboardTestCase
from springboard.utils import parse_repo_name
from springboard.tools.commands import (
    CloneRepoTool, CreateIndexTool, CreateMappingTool, SyncDataTool,
    BootstrapTool, ImportContentTool, UpdateMessagesTool)
from springboard.tools.commands.base import YAMLFile


class SpringboardToolTestCase(SpringboardTestCase):

    def mk_workspace_name(self, workspace):
        return os.path.basename(workspace.working_dir)

    def mk_workspace_config(self, workspace):
        repo_name = self.mk_workspace_name(self.workspace)
        return {
            'repositories': {
                repo_name: self.workspace.working_dir,
            }
        }


class TestYAMLHelper(SpringboardToolTestCase):

    def test_yaml_file(self):
        fp, file_name = self.mk_tempfile()
        fp.write('foo: bar\n')
        fp.close()

        argparse_type = YAMLFile()
        self.assertEqual(
            argparse_type(file_name),
            (file_name, {'foo': 'bar'}))


class TestCloneRepoTool(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_clone_repo(self):
        self.addCleanup(lambda: shutil.rmtree(self.working_dir))
        tool = CloneRepoTool()
        tool.stdout = StringIO()
        tool.run(
            config=('springboard.yaml',
                    self.mk_workspace_config(self.workspace)),
            verbose=True,
            clobber=False,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.startswith('Cloning'))
        self.assertTrue(output.endswith('test_clone_repo.\n'))

        tool.run(
            config=('springboard.yaml',
                    self.mk_workspace_config(self.workspace)),
            verbose=True,
            clobber=False,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('already exists, skipping.\n'))

        tool.run(
            config=('springboard.yaml',
                    self.mk_workspace_config(self.workspace)),
            verbose=True,
            clobber=True,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Clobbering existing repository.\n'))

        tool.run(
            config=('springboard.yaml',
                    self.mk_workspace_config(self.workspace)),
            verbose=True,
            clobber=False,
            repo_dir='%s/test_clone_repo' % (self.working_dir,),
            repo_name=None)
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('already exists, skipping.\n'))


class TestCreateIndex(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.repo = self.workspace.repo

    def test_create_index(self):
        tool = CreateIndexTool()
        tool.stdout = StringIO()
        tool.run(
            config=('springboard.yaml',
                    self.mk_workspace_config(self.workspace)),
            verbose=True,
            clobber=False,
            repo_dir=self.workspace.working_dir,
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Index already exists, skipping.\n'))

        tool.run(
            config=('springboard.yaml',
                    self.mk_workspace_config(self.workspace)),
            verbose=True,
            clobber=True,
            repo_dir=self.workspace.working_dir,
            repo_name=self.mk_workspace_name(self.workspace))
        output = tool.stdout.getvalue()
        self.assertTrue(
            output.endswith('Clobbering existing index.\nIndex created.\n'))


class TestCreateMapping(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        CreateIndexTool().create_index(self.workspace.working_dir)

    def test_create_mapping(self):
        tool = CreateMappingTool()
        tool.stdout = StringIO()

        config = self.mk_workspace_config(self.workspace)
        config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }

        tool.run(config=('springboard.yaml', config),
                 verbose=True,
                 clobber=False,
                 repo_dir=self.workspace.working_dir,
                 repo_name=self.mk_workspace_name(self.workspace))
        self.assertEqual(
            tool.stdout.getvalue(),
            'Creating mapping for elasticgit.tests.base.TestPerson.\n'
            'Mapping created.\n')


class TestSyncData(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        CreateIndexTool().create_index(self.workspace.working_dir)

    def test_sync_data(self):
        tool = SyncDataTool()
        tool.stdout = StringIO()

        config = self.mk_workspace_config(self.workspace)
        config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }

        tool.run(config=('springboard.yaml', config),
                 verbose=True,
                 clobber=False,
                 repo_dir=self.workspace.working_dir,
                 repo_name=self.mk_workspace_name(self.workspace))
        self.assertEqual(
            tool.stdout.getvalue(),
            'Syncing data for elasticgit.tests.base.TestPerson.\n'
            'Data synced.\n')


class TestBootstrapTool(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_bootstrap(self):
        tool = BootstrapTool()
        tool.stdout = StringIO()

        config = self.mk_workspace_config(self.workspace)
        config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }

        tool.run(config=('springboard.yaml', config),
                 verbose=True,
                 clobber=False,
                 repo_dir=self.working_dir)

        lines = tool.stdout.getvalue().split('\n')
        self.assertTrue(lines[0].startswith('Cloning'))
        self.assertTrue(
            lines[0].endswith(
                '%s.' % (self.mk_workspace_name(self.workspace))))
        self.assertEqual(lines[1], 'Destination already exists, skipping.')
        self.assertEqual(lines[2], 'Creating index for master.')
        self.assertEqual(lines[3], 'Index already exists, skipping.')


class TestImportContentTool(SpringboardToolTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.tool = ImportContentTool()
        self.tool.stdout = StringIO()
        self.config = self.mk_workspace_config(self.workspace)
        self.config['repositories'] = {}
        self.config['models'] = {
            'elasticgit.tests.base.TestPerson': {
                'properties': {
                    'name': {
                        'index': 'not_analyzed',
                        'type': 'string',
                    }
                }
            }
        }
        self.ini_config = self.mk_configfile({
            'app:main': {
                'unicore.content_repo_urls': '',
            }
        })
        _, self.yaml_config = self.mk_tempfile()

    def test_import_local(self):
        self.tool.run(
            config=(self.yaml_config, self.config),
            verbose=True,
            clobber=False,
            repo_dir=self.working_dir,
            repo_url=self.workspace.working_dir,
            ini_config=self.ini_config,
            ini_section='app:main',
            update_config=True,
            repo_name=None,
            repo_host=None)

        cp = ConfigParser()
        cp.read(self.ini_config)
        self.assertEqual(
            cp.get('app:main', 'unicore.content_repo_urls').strip(),
            os.path.basename(self.workspace.working_dir))

        with open(self.yaml_config, 'r') as fp:
            data = yaml.safe_load(fp)
            repo_name = parse_repo_name(self.workspace.working_dir)
            self.assertEqual(data['repositories'], {
                repo_name: self.workspace.working_dir
            })

    @responses.activate
    def test_import_remote(self):
        repo_name = parse_repo_name(self.workspace.working_dir)
        repo_location = 'http://localhost:8080/repos/%s.json' % repo_name
        responses.add_callback(
            responses.POST,
            'http://localhost:8080/repos.json',
            callback=lambda _: (301, {'Location': repo_location}, ''))

        self.tool.run(
            config=(self.yaml_config, self.config),
            verbose=True,
            clobber=False,
            repo_dir=self.working_dir,
            repo_url=self.workspace.working_dir,
            ini_config=self.ini_config,
            ini_section='app:main',
            update_config=True,
            repo_name=None,
            repo_host='http://localhost:8080')

        cp = ConfigParser()
        cp.read(self.ini_config)
        self.assertEqual(
            cp.get('app:main', 'unicore.content_repo_urls').strip(),
            repo_location)

        with open(self.yaml_config, 'r') as fp:
            data = yaml.safe_load(fp)
            self.assertEqual(data['repositories'], {
                repo_name: self.workspace.working_dir
            })


class TestUpdateMessagesTool(SpringboardToolTestCase):

    @patch('springboard.tools.commands.update_messages.run_setup')
    def test_update_messages(self, mocked_run_setup):
        tool = UpdateMessagesTool()
        tool.stdout = StringIO()
        ini_config = self.mk_configfile({
            'app:main': {
                'available_languages': 'eng_GB\npor_PT',
            }
        })
        mocked_run_setup.return_value = Mock(get_name=Mock(return_value='foo'))

        tool.run(
            ini_config=ini_config,
            ini_section='app:main',
            locales=[])

        mocked_run_setup.assert_any_call(
            'setup.py',
            ['extract_messages', '-o', 'foo/locale/messages.pot'])
        mocked_run_setup.assert_any_call(
            'setup.py',
            ['init_catalog', '-i', 'foo/locale/messages.pot',
             '-d', 'foo/locale', '-l', 'por_PT'])
        mocked_run_setup.assert_any_call(
            'setup.py',
            ['init_catalog', '-i', 'foo/locale/messages.pot',
             '-d', 'foo/locale', '-l', 'eng_GB'])
        mocked_run_setup.assert_any_call(
            'setup.py',
            ['update_catalog', '-i', 'foo/locale/messages.pot',
             '-d', 'foo/locale'])
        mocked_run_setup.assert_any_call(
            'setup.py',
            ['compile_catalog', '-d', 'foo/locale'])

        mocked_run_setup.reset_mock()
        tool.run(
            ini_config=ini_config,
            ini_section='app:main',
            locales=['swa_KE'])

        mocked_run_setup.assert_any_call(
            'setup.py',
            ['init_catalog', '-i', 'foo/locale/messages.pot',
             '-d', 'foo/locale', '-l', 'swa_KE'])
        init_calls = filter(
            lambda call: len(call[0]) > 1 and call[0][1][0] == 'init_catalog',
            mocked_run_setup.call_args_list)
        self.assertEqual(len(init_calls), 1)
