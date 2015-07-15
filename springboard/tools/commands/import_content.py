from itertools import chain
from ConfigParser import ConfigParser
from urlparse import urljoin
import json

import yaml
import requests

from springboard.utils import parse_repo_name, config_list
from springboard.tools.commands.bootstrap import BootstrapTool
from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class ImportContentTool(BootstrapTool):

    command_name = 'import'
    command_help_text = 'Clone and import a content repository.'
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
            help='Give the repository a custom name.'),
        CommandArgument(
            '-H', '--host',
            dest='repo_host',
            help='The unicore.distribute service that will host the repo.'),
    )

    def run(self, config, verbose, clobber, repo_dir, repo_url,
            ini_config, ini_section, update_config, repo_name, repo_host):
        repo_name = repo_name or parse_repo_name(repo_url)
        if repo_host:
            repo_location = self.import_remote(
                config, verbose, clobber, repo_host, repo_url, repo_name)
        else:
            repo_location = self.import_local(
                config, verbose, clobber, repo_dir, repo_url, repo_name)

        if not update_config:
            return

        config_file, config_data = config
        repositories = config_data.setdefault('repositories', {})

        if repo_name not in repositories:
            repositories[repo_name] = repo_url

            with open(config_file, 'w') as fp:
                yaml.safe_dump(config_data,
                               stream=fp, default_flow_style=False)
            self.emit('Added %s to the %s config file.' % (
                repo_name, config_file))

        config_key = 'unicore.content_repo_urls'

        cp = ConfigParser()
        cp.read(ini_config)
        if not cp.has_section(ini_section):
            cp.add_section(ini_section)

        existing_repos = (cp.get(ini_section, config_key)
                          if cp.has_option(ini_section, config_key)
                          else '')
        existing_repos = config_list(existing_repos)

        if repo_location not in existing_repos:
            cp.set(ini_section, config_key,
                   '\n'.join(chain(existing_repos, [repo_location])))
            with open(ini_config, 'w') as fp:
                cp.write(fp)
            self.emit(
                'Updated unicore.content_repo_urls in %s.' % (ini_config,))

    def import_local(self, config, verbose, clobber, repo_dir, repo_url,
                     repo_name):
        config_file, config_data = config
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
        return repo_name

    def import_remote(self, config, verbose, clobber, repo_host, repo_url,
                      repo_name):
        response = requests.post(
            urljoin(repo_host, 'repos.json'),
            data=json.dumps({
                'repo_url': repo_url,
                'repo_name': repo_name
            }),
            headers={'Content-Type': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        repo_location = response.headers['Location']
        self.emit('Created %s' % (repo_location,))
        return repo_location
