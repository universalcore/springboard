from elasticgit.utils import load_class

from springboard.tools.commands.clone import CloneRepoTool
from springboard.tools.commands.index import CreateIndexTool
from springboard.tools.commands.mapping import CreateMappingTool
from springboard.tools.commands.sync import SyncDataTool
from springboard.tools.commands.base import SpringboardToolCommand


class BootstrapTool(CloneRepoTool,
                    CreateIndexTool,
                    CreateMappingTool,
                    SyncDataTool):

    command_name = 'bootstrap'
    command_help_text = 'Tools for bootstrapping a new content repository.'
    command_arguments = SpringboardToolCommand.command_arguments

    def run(self, config, verbose, clobber, repo_dir):
        config_file, config_data = config
        all_repos = self.repositories(config_data, repo_dir)

        for repo_data in all_repos:
            self.clone_repo(repo_data['working_dir'],
                            repo_data['url'],
                            clobber=clobber,
                            verbose=verbose)

        for repo_data in all_repos:
            self.bootstrap(repo_data['working_dir'],
                           repo_data['index_prefix'],
                           models=config_data.get('models', {}).items(),
                           clobber=clobber, verbose=verbose)

    def bootstrap(self, workdir, index_prefix, models=(),
                  clobber=False, verbose=False):
        index_created = self.create_index(workdir,
                                          index_prefix,
                                          clobber=clobber,
                                          verbose=verbose)
        for model_name, mapping in models:
            model_class = load_class(model_name)
            if index_created:
                self.create_mapping(workdir, index_prefix, model_class,
                                    mapping, verbose=verbose)
            self.sync_data(workdir, index_prefix, model_class,
                           verbose=verbose, clobber=clobber)
