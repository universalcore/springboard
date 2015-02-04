import sys
import yaml

from elasticgit.commands.base import ToolCommand, CommandArgument


class YAMLFile(object):

    def __call__(self, file_name):
        with open(file_name, 'r') as fp:
            return file_name, yaml.safe_load(fp)


class SpringboardToolCommand(ToolCommand):

    command_arguments = (
        CommandArgument(
            '-c', '--config',
            dest='config',
            help='The configuration file to load',
            default='springboard.yaml',
            type=YAMLFile(),
        ),
        CommandArgument(
            '-d', '--clobber',
            dest='clobber',
            help='Clobber any existing data if it exists.',
            default=False,
            action='store_true'),
        CommandArgument(
            '-v', '--verbose',
            dest='verbose',
            help='Verbose output.',
            default=False,
            action='store_true'),
        CommandArgument(
            '-r', '--repo-dir',
            dest='repo_dir',
            help='Directory to put repositories in.',
            default='repos'),
    )

    stdout = sys.stdout
    verbose = False

    def emit(self, line):
        if self.verbose:
            self.stdout.write('%s\n' % (line,))
