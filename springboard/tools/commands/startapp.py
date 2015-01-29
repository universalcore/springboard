import pkg_resources
from cookiecutter.main import cookiecutter

from springboard.utils import parse_repo_name
from springboard.tools.commands.base import (
    SpringboardToolCommand, CommandArgument)


class StartAppTool(SpringboardToolCommand):

    command_name = 'start-app'
    command_help_text = 'Create new applicaton scaffolding'
    command_arguments = (
        CommandArgument(
            'app_name',
            metavar='app_name',
            help='The name of the application to start.'),
        CommandArgument(
            '-r', '--repo-url',
            dest='unicore_content_repo_url',
            required=True,
            help='The content repository to use.'),
        CommandArgument(
            '--security-key',
            dest='thumbor_security_key',
            default='',
            help='The thumbor security key to use.'),
        CommandArgument(
            '-a', '--author',
            dest='author',
            default='',
            help='The author\'s name.'),
        CommandArgument(
            '-e', '--author-email',
            dest='author_email',
            default='',
            help='The author\'s email address.'),
        CommandArgument(
            '--url',
            dest='url',
            default='',
            help='The project\'s URL.'),
        CommandArgument(
            '-l', '--license',
            dest='license',
            default='BSD',
            help='The application\'s licence.'),
        CommandArgument(
            '-p', '--prompt',
            dest='no_input',
            default=True,
            action='store_false')
    )

    def run(self, **options):
        if options['unicore_content_repo_url']:
            options.update({
                'unicore_content_repo_name': parse_repo_name(
                    options['unicore_content_repo_url']),
            })

        cookiecutter(
            pkg_resources.resource_filename(
                'springboard', 'tools/commands/cookiecutter/startapp'),
            no_input=options.pop('no_input'),
            extra_context=options)
