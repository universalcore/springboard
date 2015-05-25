from springboard.tools.commands.bootstrap import BootstrapTool
from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


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
    )

    def run(self, config, verbose, clobber, repo_dir,
            unicore_distribute_url):
        print unicore_distribute_url
