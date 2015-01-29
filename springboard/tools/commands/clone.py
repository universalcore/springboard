import os
import shutil

from elasticgit import EG

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class CloneRepoTool(SpringboardToolCommand):

    command_name = 'clone'
    command_help_text = 'Tools for cloning repositories.'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            'repo_name',
            metavar='repo_name',
            help='The name of the repository to clone.'),
    )

    def run(self, config, verbose, clobber, repo_dir, repo_name):
        repo_url = config['repositories'][repo_name]
        return self.clone_repo(repo_name,
                               repo_url,
                               repo_dir=repo_dir,
                               clobber=clobber,
                               verbose=verbose)

    def clone_repo(self, repo_name, repo_url,
                   repo_dir='repos', clobber=False, verbose=False):
        self.verbose = verbose
        workdir = os.path.join(repo_dir, repo_name)
        self.emit('Cloning %s to %s.' % (repo_url, workdir))
        if os.path.isdir(workdir) and not clobber:
            self.emit('Destination already exists, skipping.')
            return workdir, EG.read_repo(workdir)
        elif os.path.isdir(workdir):
            self.emit('Clobbering existing repository.')
            shutil.rmtree(workdir)

        repo = EG.clone_repo(repo_url, workdir)
        return workdir, repo
