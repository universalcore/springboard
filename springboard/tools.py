import argparse
import os
import yaml
import sys
import shutil

from elasticgit import EG
from elasticgit.commands.base import ToolCommand, CommandArgument
from elasticgit.tools import add_command, run
from elasticgit.utils import load_class, fqcn

from slugify import slugify

from springboard.utils import parse_repo_name


class YAMLFile(object):

    def __call__(self, file_name):
        with open(file_name, 'r') as fp:
            return yaml.safe_load(fp)


class SpringboardToolCommand(ToolCommand):

    command_arguments = (
        CommandArgument(
            '-d', '--clobber',
            dest='clobber',
            help='Clobber any existing data if it exists.',
            default=False,
            action='store_true'),
        CommandArgument(
            '-v', '--verbose',
            dest='verbose',
            help='Verbose output.',
            default=False,
            action='store_true'),
    )

    stdout = sys.stdout
    verbose = False

    def emit(self, line):
        if self.verbose:
            self.stdout.write('%s\n' % (line,))


class CloneRepoTool(SpringboardToolCommand):

    command_name = 'clone'
    command_help_text = 'Tools for cloning repositories.'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            'repo_url',
            metavar='repo_url',
            help='The URL of the repository to clone.'),
        CommandArgument(
            '-r', '--repo-dir',
            dest='repo_dir',
            help='Directory to put repositories in.',
            default='repos'),
    )

    def run(self, verbose, clobber, repo_url, repo_dir):
        return self.clone_repo(repo_url,
                               repo_dir=repo_dir,
                               clobber=clobber,
                               verbose=verbose)

    def clone_repo(self, repo_url, repo_dir='repos',
                   clobber=False, verbose=False):
        self.verbose = verbose
        workdir = os.path.join(repo_dir, parse_repo_name(repo_url))
        self.emit('Cloning %s to %s.' % (repo_url, workdir))
        if os.path.isdir(workdir) and not clobber:
            self.emit('Destination already exists, skipping.')
            return workdir, EG.read_repo(workdir)
        elif os.path.isdir(workdir):
            self.emit('Clobbering existing repository.')
            shutil.rmtree(workdir)

        repo = EG.clone_repo(repo_url, workdir)
        return workdir, repo


class CreateIndexTool(SpringboardToolCommand):

    command_name = 'create-index'
    command_help_text = 'Create an Elasticsearch for a repository'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            'repo_dir',
            metavar='repo_dir',
            help='The repository directory'),
    )

    def run(self, verbose, clobber, repo_dir):
        return self.create_index(repo_dir, verbose=verbose, clobber=clobber)

    def create_index(self, workdir, verbose=False, clobber=False):
        self.verbose = verbose
        workspace = EG.workspace(
            workdir, index_prefix=slugify(os.path.basename(workdir)))
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


class CreateMappingTool(SpringboardToolCommand):

    command_name = 'create-mapping'
    command_help_text = 'Upload a mapping for models stored in elastic-git'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            '-c', '--config',
            dest='config',
            help='The config file to use for cloning.',
            default='bootstrap.yaml',
            type=YAMLFile()),
        CommandArgument(
            '-r', '--repo-dir',
            dest='repo_dir',
            help='Directory to put repositories in.',
            default='repos'),
    )

    def run(self, verbose, clobber, config, repo_dir):
        for model_name, mapping in config['models'].items():
            model_class = load_class(model_name)
            self.create_mapping(repo_dir, model_class, mapping,
                                verbose=verbose)

    def create_mapping(self, repo_dir, model_class, mapping,
                       verbose=False):
        self.verbose = verbose
        workspace = EG.workspace(
            repo_dir, index_prefix=slugify(os.path.basename(repo_dir)))
        self.emit('Creating mapping for %s.' % (fqcn(model_class),))
        workspace.setup_custom_mapping(model_class, mapping)
        self.emit('Mapping created.')


class SyncDataTool(SpringboardToolCommand):

    command_name = 'sync-data'
    command_help_text = 'Sync data from a repo with elastic-git'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            '-c', '--config',
            dest='config',
            help='The config file to use for cloning.',
            default='bootstrap.yaml',
            type=YAMLFile()),
        CommandArgument(
            'repo_dir',
            metavar='repo_dir',
            help='The git repository direction to read data from.'),
    )

    def run(self, verbose, clobber, config, repo_dir):
        for model_name, mapping in config['models'].items():
            model_class = load_class(model_name)
            self.sync_data(repo_dir, model_class,
                           verbose=verbose,
                           clobber=clobber)

    def sync_data(self, workdir, model_class, verbose=False, clobber=False):
        self.verbose = verbose
        workdir = EG.workspace(
            workdir, index_prefix=slugify(os.path.basename(workdir)))
        self.emit('Syncing data for %s.' % (fqcn(model_class),))
        workdir.sync(model_class)
        self.emit('Data synced.')


class BootstrapTool(CloneRepoTool,
                    CreateIndexTool,
                    CreateMappingTool,
                    SyncDataTool):

    command_name = 'bootstrap'
    command_help_text = 'Tools for bootstrapping a new content repository.'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            '-c', '--config',
            dest='config',
            help='The config file to use for cloning.',
            default='bootstrap.yaml',
            type=YAMLFile()),
        CommandArgument(
            '-r', '--repo-dir',
            dest='repo_dir',
            help='Directory to put repositories in.',
            default='repos'),
    )

    def run(self, verbose, clobber, config, repo_dir):
        repos = [self.clone_repo(repo_url,
                                 repo_dir=repo_dir,
                                 clobber=clobber,
                                 verbose=verbose)
                 for repo_url in config['repositories']]
        for workdir, _ in repos:
            index_created = self.create_index(workdir,
                                              clobber=clobber,
                                              verbose=verbose)
            for model_name, mapping in config['models'].items():
                model_class = load_class(model_name)
                if index_created:
                    self.create_mapping(workdir, model_class, mapping)
                self.sync_data(workdir, model_class)


def get_parser():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Springboard command line tools.")
    subparsers = parser.add_subparsers(help='Commands')

    add_command(subparsers, BootstrapTool)
    add_command(subparsers, CloneRepoTool)
    add_command(subparsers, CreateIndexTool)
    add_command(subparsers, CreateMappingTool)
    add_command(subparsers, SyncDataTool)
    return parser


def main():  # pragma: no cover
    run(get_parser())
