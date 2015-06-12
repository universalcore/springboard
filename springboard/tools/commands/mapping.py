from elasticgit import EG
from elasticgit.utils import load_class, fqcn

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class CreateMappingTool(SpringboardToolCommand):

    command_name = 'create-mapping'
    command_help_text = 'Upload a mapping for models stored in elastic-git'
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
            for model_name, mapping in config_data.get('models', {}).items():
                model_class = load_class(model_name)
                self.create_mapping(repo_data['working_dir'],
                                    repo_data['index_prefix'],
                                    model_class,
                                    mapping,
                                    verbose=verbose)

    def create_mapping(self, workdir, index_prefix, model_class, mapping,
                       verbose=False):
        self.verbose = verbose
        workspace = EG.workspace(workdir, index_prefix=index_prefix)
        self.emit('Creating mapping for %s.' % (fqcn(model_class),))
        workspace.setup_custom_mapping(model_class, mapping)
        self.emit('Mapping created.')
