from itertools import chain
from ConfigParser import ConfigParser

import yaml

from springboard.utils import parse_repo_name, config_list
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
    )

    def run(self, config, verbose, clobber, repo_dir, repo_url,
            ini_config, ini_section, update_config, repo_name):
        config_file, config_data = config
        repo_name = repo_name or parse_repo_name(repo_url)
        workdir, _ = self.clone_repo(repo_name=repo_name,
                                     repo_url=repo_url,
                                     repo_dir=repo_dir,
                                     clobber=clobber,
                                     verbose=verbose)
        self.bootstrap(
            workdir,
            config_data.get('models', {}).items(),
            clobber=clobber,
            verbose=verbose)

        if not update_config:
            return

        repositories = config_data.setdefault('repositories', {})

        if repo_name not in repositories:
            repositories[repo_name] = repo_url

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

        existing_repo_names = (cp.get(ini_section, config_key)
                               if cp.has_option(ini_section, config_key)
                               else '')
        existing_repo_names = config_list(existing_repo_names)

        if repo_name not in existing_repo_names:
            cp.set(ini_section, config_key,
                   '\n'.join(chain(existing_repo_names, [repo_name])))
            with open(ini_config, 'w') as fp:
                cp.write(fp)
            self.emit(
                'Updated unicore.content_repos in %s.' % (ini_config,))
