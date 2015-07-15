import os

from elasticgit import EG

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class CreateIndexTool(SpringboardToolCommand):

    command_name = 'create-index'
    command_help_text = (
        'Create a search index for models stored in elastic-git')
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            'repo_name',
            metavar='repo_name',
            help='The repository name'),
    )

    def run(self, config, verbose, clobber, repo_dir, repo_name):
        return self.create_index(os.path.join(repo_dir, repo_name),
                                 verbose=verbose, clobber=clobber)

    def create_index(self, workdir, verbose=False, clobber=False):
        self.verbose = verbose
        workspace = EG.workspace(
            workdir, index_prefix=os.path.basename(workdir))
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
