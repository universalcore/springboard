import shutil
from StringIO import StringIO

from springboard.tests import SpringboardTestCase
from springboard.tools import (
    CloneRepoTool, CreateIndexTool, CreateMappingTool, SyncDataTool,
    BootstrapTool)


class TestCloneRepoTool(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_clone_repo(self):
        self.addCleanup(lambda: shutil.rmtree(self.working_dir))
        tool = CloneRepoTool()
        tool.stdout = StringIO()
        tool.run(
            verbose=True,
            clobber=False,
            repo_url=self.workspace.working_dir,
            repo_dir='%s/test_clone_repo' % (self.working_dir,))
        output = tool.stdout.getvalue()
        self.assertTrue(output.startswith('Cloning'))
        self.assertTrue(output.endswith('test_clone_repo.\n'))

        tool.run(
            verbose=True,
            clobber=False,
            repo_url=self.workspace.working_dir,
            repo_dir='%s/test_clone_repo' % (self.working_dir,))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('already exists, skipping.\n'))

        tool.run(
            verbose=True,
            clobber=True,
            repo_url=self.workspace.working_dir,
            repo_dir='%s/test_clone_repo' % (self.working_dir,))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Clobbering existing repository.\n'))


class TestCreateIndex(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        self.repo = self.workspace.repo

    def test_create_index(self):
        tool = CreateIndexTool()
        tool.stdout = StringIO()
        tool.run(
            verbose=True,
            clobber=False,
            repo_dir=self.workspace.working_dir)
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Index already exists, skipping.\n'))

        tool.run(
            verbose=True,
            clobber=True,
            repo_dir=self.workspace.working_dir)
        output = tool.stdout.getvalue()
        self.assertTrue(
            output.endswith('Clobbering existing index.\nIndex created.\n'))


class TestCreateMapping(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        CreateIndexTool().create_index(self.workspace.working_dir)

    def test_create_mapping(self):
        tool = CreateMappingTool()
        tool.stdout = StringIO()
        tool.run(verbose=True,
                 clobber=False,
                 config={
                     'models': {
                         'elasticgit.tests.base.TestPerson': {
                             'properties': {
                                 'name': {
                                     'index': 'not_analyzed',
                                     'type': 'string',
                                 }
                             }
                         }
                     }
                 },
                 repo_dir=self.workspace.working_dir)
        self.assertEqual(
            tool.stdout.getvalue(),
            'Creating mapping for elasticgit.tests.base.TestPerson.\n'
            'Mapping created.\n')


class TestSyncData(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()
        CreateIndexTool().create_index(self.workspace.working_dir)

    def test_sync_data(self):
        tool = SyncDataTool()
        tool.stdout = StringIO()
        tool.run(verbose=True,
                 clobber=False,
                 config={
                     'models': {
                         'elasticgit.tests.base.TestPerson': {
                             'properties': {
                                 'name': {
                                     'index': 'not_analyzed',
                                     'type': 'string',
                                 }
                             }
                         }
                     }
                 },
                 repo_dir=self.workspace.working_dir)
        self.assertEqual(
            tool.stdout.getvalue(),
            'Syncing data for elasticgit.tests.base.TestPerson.\n'
            'Data synced.\n')


class TestBootstrapTool(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_bootstrap(self):
        tool = BootstrapTool()
        tool.stdout = StringIO()
        tool.run(verbose=True,
                 clobber=False,
                 config={
                     'repositories': [self.workspace.working_dir],
                     'models': {
                         'elasticgit.tests.base.TestPerson': {
                             'properties': {
                                 'name': {
                                     'index': 'not_analyzed',
                                     'type': 'string',
                                 }
                             }
                         }
                     }
                 }, repo_dir=self.working_dir)

        output = tool.stdout.getvalue()
        self.assertTrue(output.startswith('Cloning'))
        self.assertTrue(output.endswith(
            'Destination already exists, skipping.\n'
            'Creating index for master.\n'
            'Index already exists, skipping.\n'))
