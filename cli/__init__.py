import importlib
import os


def register_cli_commands(app):
    """
    Register 0 or more Flask CLI commands (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename.endswith('.py') and filename.startswith('cmd_'):
            module = importlib.import_module(f'cli.{filename[:-3]}')
            cmd = getattr(module, filename[4:-3])
            app.cli.add_command(cmd)

    return None
