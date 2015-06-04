from springboard.tools.commands.bootstrap import BootstrapTool
from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)

from springboard.utils import config_list


class ConnectTool(BootstrapTool):

    command_name = 'connect'
    command_help_text = (
        'Connect to a unicore.distribute server and use one of the content '
        'repositories made available on it.')
    command_arguments = SpringboardToolCommand.command_arguments + (
        CommandArgument(
            'unicore_distribute_url',
            metavar='unicore_distribute_url',
            help='The URL of the unicore.distribute content repository.'),
        CommandArgument(
            '-i', '--ini',
            dest='ini_config',
            default='development.ini',
            help='The paste ini file to update'),
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
    )

    def run(self, config, verbose, clobber, repo_dir,
            unicore_distribute_url, ini_config, ini_section, update_config):
        config_file, config_data = config

        if not update_config:
            return

        config_key = 'unicore.distribute.content_repo_urls'
        cp = ConfigParser()
        cp.read(ini_config)
        if not cp.has_section(ini_section):
            cp.add_section(ini_section)

        existing_content_repo_urls = config_list(
            cp.get(ini_section, config_key)
            if cp.has_option(ini_section, config_key)
            else '')

        if unicore_distribute_url not in existing_content_repo_urls:
            cp.set(
                ini_section, config_key, '\n'.join(
                    chain(
                        existing_repo_urls, [unicore_distribute_url])))
            with open(ini_config, 'w') as fp:
                cp.write(fp)
            self.emit(
                'Updated unicore.')