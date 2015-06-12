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
            '-rn', '--repo-name',
            dest='repo_name',
            help='The name of the repository to clone.'),
    )

    def run(self, config, verbose, clobber, repo_dir, repo_name):
        config_file, config_data = config
        repo_names = [repo_name] if repo_name else []
        repos = [self.clone_repo(repo_data['working_dir'],
                                 repo_data['url'],
                                 clobber=clobber,
                                 verbose=verbose)
                 for repo_data in self.iter_repositories(config_data,
                                                         repo_dir,
                                                         *repo_names)]
        return repos

    def clone_repo(self, workdir, repo_url, clobber=False, verbose=False):
        self.verbose = verbose
        self.emit('Cloning %s to %s.' % (repo_url, workdir))
        if os.path.isdir(workdir) and not clobber:
            self.emit('Destination already exists, skipping.')
            return workdir, EG.read_repo(workdir)
        elif os.path.isdir(workdir):
            self.emit('Clobbering existing repository.')
            shutil.rmtree(workdir)

        repo = EG.clone_repo(repo_url, workdir)
        return workdir, repo
