import os

from ConfigParser import ConfigParser

import yaml
from slugify import slugify

from springboard.utils import parse_repo_name, config_dict
from springboard.tools.commands.bootstrap import BootstrapTool
from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class ImportContentTool(BootstrapTool):

    command_name = 'import'
    command_help_text = 'Clone and import a content repository locally.'
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            'repo_url',
            metavar='repo_url',
            help='The URL of the Git content repository to clone.'),
        CommandArgument(
            '-i', '--ini',
            dest='ini_config',
            default='development.ini',
            help='The paste ini file to update.'),
        CommandArgument(
            '-s', '--ini-section',
            dest='ini_section',
            default='app:main',
            help='The paste ini section to update'),
        CommandArgument(
            '-u', '--update-config',
            dest='update_config',
            default=True,
            help='Add the repository to the config files?',
            action='store_false'),
        CommandArgument(
            '-n', '--name',
            dest='repo_name',
            help='Give the repository a custom name on disk.'),
        CommandArgument(
            '-p', '--index-prefix',
            dest='index_prefix',
            help='Use a custom index prefix for the repository on ES.')
    )

    def run(self, config, verbose, clobber, repo_dir, repo_url,
            ini_config, ini_section, update_config, repo_name,
            index_prefix):
        config_file, config_data = config
        repo_name = repo_name or parse_repo_name(repo_url)
        workdir = os.path.join(repo_dir, repo_name)
        index_prefix = index_prefix or slugify(repo_name)
        self.clone_repo(workdir=workdir,
                        repo_url=repo_url,
                        clobber=clobber,
                        verbose=verbose)
        self.bootstrap(
            workdir,
            index_prefix,
            config_data.get('models', {}).items(),
            clobber=clobber,
            verbose=verbose)

        if not update_config:
            return

        repositories = config_data.setdefault('repositories', {})

        if repo_name not in repositories:
            repositories[repo_name] = {
                'url': repo_url,
                'index_prefix': index_prefix
            }

            with open(config_file, 'w') as fp:
                yaml.safe_dump(config_data,
                               stream=fp, default_flow_style=False)
            self.emit('Added %s to the %s config file.' % (
                repo_name, config_file))

        config_key = 'unicore.content_repos'

        cp = ConfigParser()
        cp.read(ini_config)
        if not cp.has_section(ini_section):
            cp.add_section(ini_section)

        existing_repos = (cp.get(ini_section, config_key)
                          if cp.has_option(ini_section, config_key)
                          else '')
        existing_repos = config_dict(existing_repos)
        existing_repos[repo_name] = index_prefix
        cp.set(
            ini_section, config_key,
            '\n'.join('%s = %s' % (k, v) for k, v in existing_repos.items()))
        with open(ini_config, 'w') as fp:
            cp.write(fp)
        self.emit(
            'Updated unicore.content_repos in %s.' % (ini_config,))
