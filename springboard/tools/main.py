import argparse

from elasticgit.tools import add_command, run

from springboard.tools.commands import CloneRepoTool
from springboard.tools.commands import CreateIndexTool
from springboard.tools.commands import CreateMappingTool
from springboard.tools.commands import SyncDataTool
from springboard.tools.commands import BootstrapTool
from springboard.tools.commands import StartAppTool
from springboard.tools.commands import ImportContentTool


def get_parser():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Springboard command line tools.")
    subparsers = parser.add_subparsers(help='Commands')

    add_command(subparsers, BootstrapTool)
    add_command(subparsers, CloneRepoTool)
    add_command(subparsers, CreateIndexTool)
    add_command(subparsers, CreateMappingTool)
    add_command(subparsers, SyncDataTool)
    add_command(subparsers, StartAppTool)
    add_command(subparsers, ImportContentTool)
    return parser


def main():  # pragma: no cover
    run(get_parser())
