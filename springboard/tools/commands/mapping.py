import os

from elasticgit import EG
from elasticgit.utils import load_class, fqcn

from slugify import slugify

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class CreateMappingTool(SpringboardToolCommand):

    command_name = 'create-mapping'
    command_help_text = 'Upload a mapping for models stored in elastic-git'
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
            self.create_mapping(os.path.join(repo_dir, repo_name),
                                model_class, mapping,
                                es={'urls': es_hosts}, verbose=verbose)

    def create_mapping(self, repo_dir, model_class, mapping,
                       es={}, verbose=False):
        self.verbose = verbose
        workspace = EG.workspace(
            repo_dir, es=es, index_prefix=slugify(os.path.basename(repo_dir)))
        self.emit('Creating mapping for %s.' % (fqcn(model_class),))
        workspace.setup_custom_mapping(model_class, mapping)
        self.emit('Mapping created.')
