from elasticgit.utils import load_class

from springboard.tools.commands.clone import CloneRepoTool
from springboard.tools.commands.index import CreateIndexTool
from springboard.tools.commands.mapping import CreateMappingTool
from springboard.tools.commands.sync import SyncDataTool


class BootstrapTool(CloneRepoTool,
                    CreateIndexTool,
                    CreateMappingTool,
                    SyncDataTool):

    command_name = 'bootstrap'
    command_help_text = 'Tools for bootstrapping a new content repository.'

    def run(self, config, verbose, clobber, repo_dir):
        repos = [self.clone_repo(repo_name=repo_name,
                                 repo_url=repo_url,
                                 repo_dir=repo_dir,
                                 clobber=clobber,
                                 verbose=verbose)
                 for repo_name, repo_url in config['repositories'].items()]
        for workdir, _ in repos:
            index_created = self.create_index(workdir,
                                              clobber=clobber,
                                              verbose=verbose)
            for model_name, mapping in config['models'].items():
                model_class = load_class(model_name)
                if index_created:
                    self.create_mapping(workdir, model_class, mapping)
                self.sync_data(workdir, model_class)
