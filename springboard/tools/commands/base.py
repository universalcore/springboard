import os
import sys
import yaml

from slugify import slugify

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

    def iter_repositories(self, config_data, repo_dir, *repo_names):
        if not repo_names:
            repo_names = config_data['repositories'].keys()

        for repo_name in repo_names:
            repo_data = config_data['repositories'][repo_name]
            yield {
                'name': repo_name,
                'working_dir': os.path.join(repo_dir, repo_name),
                'url': repo_data['url'],
                'index_prefix': repo_data.get(
                    'index_prefix', slugify(repo_name))
            }

    def repositories(self, config_data, repo_dir, *repo_names):
        return [data for data
                in self.iter_repositories(config_data, repo_dir, *repo_names)]
