from elasticgit import EG

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class CreateIndexTool(SpringboardToolCommand):

    command_name = 'create-index'
    command_help_text = (
        'Create a search index for models stored in elastic-git')
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            '-rn', '--repo-name',
            dest='repo_name',
            help='The name of the repository.'),
    )

    def run(self, config, verbose, clobber, repo_dir, repo_name):
        config_file, config_data = config
        repo_names = [repo_name] if repo_name else []
        for repo_data in self.iter_repositories(config_data,
                                                repo_dir,
                                                *repo_names):
            return self.create_index(repo_data['working_dir'],
                                     repo_data['index_prefix'],
                                     verbose=verbose,
                                     clobber=clobber)

    def create_index(self, workdir, index_prefix,
                     verbose=False, clobber=False):
        self.verbose = verbose
        workspace = EG.workspace(workdir, index_prefix=index_prefix)
        branch = workspace.repo.active_branch
        self.emit('Creating index for %s.' % (branch.name,))
        if workspace.im.index_exists(branch.name) and not clobber:
            self.emit('Index already exists, skipping.')
            return False
        elif workspace.im.index_exists(branch.name) and clobber:
            self.emit('Clobbering existing index.')
            workspace.im.destroy_index(branch.name)

        workspace.im.create_index(branch.name)
        while not workspace.index_ready():
            pass

        self.emit('Index created.')
        return True
