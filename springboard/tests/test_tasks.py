from pyramid import testing

from mock import patch, MagicMock

from springboard.tests.base import SpringboardTestCase
from springboard.tasks import pull
from springboard.utils import repo_url


class TestTasks(SpringboardTestCase):

    def setUp(self):
        self.config = testing.setUp()
        celery_config = self.mk_configfile({
            'celery': {
                'celery_always_eager': 'true'}
            })
        self.config.include('pyramid_celery')
        self.config.configure_celery(celery_config)

    def tearDown(self):
        testing.tearDown()

    @patch('springboard.tasks.RemoteStorageManager')
    @patch('springboard.tasks.EG.workspace')
    def test_pull(self, mocked_workspace_init, mocked_rsm_init):
        local_repo_url = repo_url('repos', 'foo')
        remote_repo_url = repo_url('repos', 'http://localhost/repos/foo.json')
        es = {'urls': ['http://host:port']}
        mocked_workspace = MagicMock()
        mocked_workspace_init.return_value = mocked_workspace
        mocked_rsm = MagicMock()
        mocked_rsm_init.return_value = mocked_rsm

        pull.delay(local_repo_url, index_prefix='foo', es=es)
        mocked_workspace_init.assert_called_once_with(
            local_repo_url,
            index_prefix='foo',
            es=es)
        self.assertEqual(mocked_workspace.pull.call_count, 1)
        self.assertFalse(mocked_rsm_init.called)

        mocked_workspace_init.reset_mock()
        pull.delay(remote_repo_url, index_prefix='foo', es=es)
        mocked_rsm_init.assert_called_once_with(remote_repo_url)
        self.assertEqual(mocked_rsm.pull.call_count, 1)
        self.assertFalse(mocked_workspace_init.called)
