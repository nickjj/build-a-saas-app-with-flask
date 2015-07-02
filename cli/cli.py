import logging
import os
import sys

import click

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))


class CLI(click.MultiCommand):
    def list_commands(self, ctx):
        """
        Obtain a list of all available commands.

        :param ctx: Click context
        :return: List of commands
        """
        commands = []

        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
                    filename.startswith('cmd_'):
                commands.append(filename[4:-3])
        commands.sort()

        return commands

    def get_command(self, ctx, name):
        """
        Get a specific command by looking up the module.

        :param ctx: Click context
        :param name: Command name
        :return: Module's cli function
        """
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('cli.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError as e:
            logging.error('Error importing module {0}:\n{0}'.format(name, e))
            exit(1)

        return mod.cli


@click.command(cls=CLI)
def cli():
    """ Commands to help manage your project. """
    pass
