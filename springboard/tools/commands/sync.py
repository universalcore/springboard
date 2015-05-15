import os

from elasticgit import EG
from elasticgit.utils import load_class, fqcn

from slugify import slugify

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class SyncDataTool(SpringboardToolCommand):

    command_name = 'sync-data'
    command_help_text = 'Sync data from a repo with elastic-git'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            '-eh', '--es-host',
            dest='es_hosts',
            help='The Elasticsearch host.',
            default=['http://localhost:9200/'],
            nargs='+'
        ),
        CommandArgument(
            'repo_name',
            metavar='repo_name',
            help='The repository name'),
    )

    def run(self, config, verbose, clobber, repo_dir, es_hosts, repo_name):
        config_file, config_data = config
        for model_name, mapping in config_data.get('models', {}).items():
            model_class = load_class(model_name)
            self.sync_data(os.path.join(repo_dir, repo_name), model_class,
                           es={'urls': es_hosts}, verbose=verbose,
                           clobber=clobber)

    def sync_data(self, workdir, model_class, es={}, verbose=False,
                  clobber=False):
        self.verbose = verbose
        workdir = EG.workspace(
            workdir, es=es, index_prefix=slugify(os.path.basename(workdir)))
        self.emit('Syncing data for %s.' % (fqcn(model_class),))
        workdir.sync(model_class)
        self.emit('Data synced.')
