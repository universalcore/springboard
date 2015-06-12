from elasticgit import EG
from elasticgit.utils import load_class, fqcn

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class SyncDataTool(SpringboardToolCommand):

    command_name = 'sync-data'
    command_help_text = 'Sync data from a repo with elastic-git'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            '-rn', '--repo-name',
            dest='repo_name',
            help='The name of the repository to sync.'),
    )

    def run(self, config, verbose, clobber, repo_dir, repo_name):
        config_file, config_data = config
        repo_names = [repo_name] if repo_name else []
        for repo_data in self.iter_repositories(config_data,
                                                repo_dir,
                                                *repo_names):
            for model_name, mapping in config_data.get('models', {}).items():
                model_class = load_class(model_name)
                self.sync_data(repo_data['working_dir'],
                               repo_data['index_prefix'],
                               model_class,
                               verbose=verbose,
                               clobber=clobber)

    def sync_data(self, workdir, index_prefix, model_class,
                  verbose=False, clobber=False):
        self.verbose = verbose
        workdir = EG.workspace(workdir, index_prefix=index_prefix)
        self.emit('Syncing data for %s.' % (fqcn(model_class),))
        workdir.sync(model_class)
        self.emit('Data synced.')
