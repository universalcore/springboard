import os

from elasticgit import EG

from slugify import slugify

from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class CreateIndexTool(SpringboardToolCommand):

    command_name = 'create-index'
    command_help_text = (
        'Create a search index for models stored in elastic-git')
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
        return self.create_index(os.path.join(repo_dir, repo_name),
                                 verbose=verbose, clobber=clobber,
                                 es={'urls': es_hosts})

    def create_index(self, workdir, verbose=False, clobber=False,
                     es={}):
        self.verbose = verbose
        workspace = EG.workspace(
            workdir, es=es, index_prefix=slugify(os.path.basename(workdir)))
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
