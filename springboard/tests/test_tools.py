import shutil
from StringIO import StringIO

from springboard.tests import SpringboardTestCase
from springboard.tools import CloneRepoTool


class TestCloneRepoTool(SpringboardTestCase):

    def setUp(self):
        self.workspace = self.mk_workspace()

    def test_clone_repo(self):
        self.addCleanup(lambda: shutil.rmtree(self.working_dir))
        tool = CloneRepoTool()
        tool.stdout = StringIO()
        tool.run(
            self.workspace.working_dir,
            verbose=True,
            clobber=False,
            repodir='%s/test_clone_repo' % (self.working_dir,))
        output = tool.stdout.getvalue()
        self.assertTrue(output.startswith('Cloning'))
        self.assertTrue(output.endswith('test_clone_repo.\n'))

        tool.run(
            self.workspace.working_dir,
            verbose=True,
            clobber=False,
            repodir='%s/test_clone_repo' % (self.working_dir,))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('already exists, skipping.\n'))

        tool.run(
            self.workspace.working_dir,
            verbose=True,
            clobber=True,
            repodir='%s/test_clone_repo' % (self.working_dir,))
        output = tool.stdout.getvalue()
        self.assertTrue(output.endswith('Clobbering existing repository.\n'))
