import argparse
import os
import yaml
import sys
import shutil

from elasticgit import EG
from elasticgit.commands.base import ToolCommand, CommandArgument
from elasticgit.tools import add_command, run
from elasticgit.utils import load_class, fqcn

from springboard.utils import parse_repo_name


class YAMLFile(object):

    def __call__(self, file_name):
        with open(file_name, 'r') as fp:
            return yaml.safe_load(fp)


class BootstrapTool(ToolCommand):

    command_name = 'bootstrap'
    command_help_text = 'Tools for bootstrapping a new content repository.'
    command_arguments = (
        CommandArgument(
            '-c', '--config',
            dest='config',
            help='The config file to use for bootstrapping.',
            default='unicore.yaml',
            type=YAMLFile()),
        CommandArgument(
            '-v', '--verbose',
            dest='verbose',
            help='Verbose output.',
            default=False,
            action='store_true'),
        CommandArgument(
            '-d', '--clobber',
            dest='clobber',
            help='Clobber any existing data if it exists.',
            default=False,
            action='store_true'),
    )

    stdout = sys.stdout

    def run(self, config, verbose, clobber):
        self.verbose = verbose

        repos = [self.clone_repo(repo_url, clobber=clobber)
                 for repo_url in config['repositories']]
        for workdir, _ in repos:
            index_created = self.create_index(workdir, clobber=clobber)
            for model_name, mapping in config['models'].items():
                model_class = load_class(model_name)
                if index_created:
                    self.create_mapping(workdir, model_class, mapping)
                self.sync_data(workdir, model_class)

    def emit(self, line):
        if self.verbose:
            self.stdout.write('%s\n' % (line,))

    def clone_repo(self, repo_url, clobber=False):
        workdir = os.path.join('repos', parse_repo_name(repo_url))
        self.emit('Cloning %s to %s.' % (repo_url, workdir))
        if os.path.isdir(workdir) and not clobber:
            self.emit('Destination already exists, skipping.')
            return workdir, EG.read_repo(workdir)
        elif os.path.isdir(workdir):
            self.emit('Clobbering existing repository.')
            shutil.rmtree(workdir)

        repo = EG.clone_repo(repo_url, workdir)
        return workdir, repo

    def create_index(self, workdir, clobber=False):
        workspace = EG.workspace(workdir)
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

    def create_mapping(self, workdir, model_class, mapping):
        workspace = EG.workspace(workdir)
        self.emit('Creating mapping for %s.' % (fqcn(model_class),))
        workspace.setup_custom_mapping(model_class, mapping)
        self.emit('Mapping created.')

    def sync_data(self, workdir, model_class):
        workdir = EG.workspace(workdir)
        self.emit('Syncing data for %s.' % (fqcn(model_class),))
        workdir.sync(model_class)
        self.emit('Data synced.')


def get_parser():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Springboard command line tools.")
    subparsers = parser.add_subparsers(help='Commands')

    add_command(subparsers, BootstrapTool)

    return parser


def main():  # pragma: no cover
    run(get_parser())
