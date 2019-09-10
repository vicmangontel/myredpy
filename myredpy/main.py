import os
from tinydb import TinyDB
from redminelib import Redmine
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from cement.utils import fs
from .core.exc import MyRedPyAppError
from .controllers.base import Base
from .controllers.projects import Projects
from .controllers.time_entries import TimeEntries
from .controllers.settings import Settings

# configuration defaults
CONFIG = init_defaults('myredpy', 'log.logging')
CONFIG['myredpy']['redmine_url'] = ''
CONFIG['myredpy']['redmine_key'] = ''
CONFIG['myredpy']['db_file'] = '~/.myredpy/db.json'


def extend_redmine(app):
    app.log.debug('Connecting to redmine...')
    redmine_url = app.config.get('myredpy', 'redmine_url')
    redmine_key = app.config.get('myredpy', 'redmine_key')
    redmine = Redmine(redmine_url, key=redmine_key)
    app.extend('redmine', redmine)


def extend_tinydb(app):
    db_file = app.config.get('myredpy', 'db_file')
    # expand full path
    db_file = fs.abspath(db_file)
    app.log.debug('Tiny db file is {}'.format(db_file))
    # ensure path exists
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.extend('db', TinyDB(db_file))


class MyRedPyApp(App):
    """MyRedPy primary application."""

    class Meta:
        label = 'myredpy'

        hooks = [
            ('post_setup', extend_tinydb),
            ('pre_run', extend_redmine)
        ]

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'tabulate'
        ]

        # configuration defaults
        config_defaults = CONFIG
        config_handler = 'yaml'
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'tabulate'

        # register handlers
        handlers = [
            Base,
            Projects,
            TimeEntries,
            Settings
        ]


class MyRedPyAppTest(TestApp, MyRedPyApp):
    """A sub-class of MyRedPyApp that is better suited for testing."""

    class Meta:
        label = 'myredpy'


def main():
    with MyRedPyApp() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except MyRedPyAppError as e:
            print('MyRedPyAppError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
