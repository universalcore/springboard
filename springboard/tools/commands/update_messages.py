import os
import glob
from distutils.core import run_setup
from ConfigParser import ConfigParser

from springboard.utils import config_list
from springboard.tools.commands.base import ToolCommand, CommandArgument


class UpdateMessagesTool(ToolCommand):

    command_name = 'update-messages'
    command_help_text = 'Update or create .po and .mo message files'
    command_arguments = (
        CommandArgument(
            '-i', '--ini',
            dest='ini_config',
            default='development.ini',
            help='The paste ini file to get the locales from.'),
        CommandArgument(
            '-s', '--ini-section',
            dest='ini_section',
            default='app:main',
            help='The paste ini section to get the locales from.'),
        CommandArgument(
            '-l', '--locale',
            dest='locales',
            nargs='*',
            help='The locales to update or create.'),
    )

    def run(self, ini_config, ini_section, locales):
        if not locales:
            cp = ConfigParser()
            cp.read(ini_config)
            locales = config_list(cp.get(ini_section, 'available_languages'))

        package_name = run_setup('setup.py', stop_after='init').get_name()
        locale_dir = os.path.join(package_name, 'locale')
        pot_filename = os.path.join(locale_dir, 'messages.pot')

        # delete existing .mo files
        for filename in glob.glob(
                os.path.join(locale_dir, '*/LC_MESSAGES/*.mo')):
            os.remove(filename)

        # generate new .pot file
        run_setup('setup.py', [
            'extract_messages', '-o', pot_filename])

        # initialize new locales' .po files
        for locale in locales:
            po_filename = os.path.join(
                locale_dir, '%s/LC_MESSAGES/messages.po' % locale)
            if os.path.exists(po_filename):
                continue
            run_setup('setup.py', [
                'init_catalog', '-i', pot_filename, '-d', locale_dir,
                '-l', locale])

        # update and compile .po files
        run_setup('setup.py', [
            'update_catalog', '-i', pot_filename, '-d', locale_dir])
        run_setup('setup.py', [
            'compile_catalog', '-d', locale_dir])
