import os
import shutil
from ConfigParser import ConfigParser
from StringIO import StringIO

import yaml

from springboard.tests import SpringboardTestCase
from springboard.utils import parse_repo_name
from springboard.tools.commands import (
    CloneRepoTool, CreateIndexTool, CreateMappingTool, SyncDataTool,
    BootstrapTool, ImportContentTool)
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

    def test_import(self):
        tool = ImportContentTool()
        tool.stdout = StringIO()
        config = self.mk_workspace_config(self.workspace)
        config['repositories'] = {}
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

        ini_config = self.mk_configfile({
            'app:main': {
                'unicore.content_repos': '',
            }
        })

        _, yaml_config = self.mk_tempfile()
        tool.run(config=(yaml_config, config),
                 verbose=True,
                 clobber=False,
                 repo_dir=self.working_dir,
                 repo_url=self.workspace.working_dir,
                 ini_config=ini_config,
                 ini_section='app:main',
                 update_config=True,
                 repo_name=None)

        cp = ConfigParser()
        cp.read(ini_config)
        self.assertEqual(
            cp.get('app:main', 'unicore.content_repos').strip(),
            os.path.basename(self.workspace.working_dir))

        with open(yaml_config, 'r') as fp:
            data = yaml.safe_load(fp)
            repo_name = parse_repo_name(self.workspace.working_dir)
            self.assertEqual(data['repositories'], {
                repo_name: self.workspace.working_dir
            })
