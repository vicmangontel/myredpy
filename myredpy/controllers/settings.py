from tinydb import Query
from cement import Controller, ex
from myredpy.core.settings_name import (OMITT_PREFIX_SETTING, IGNORED_PROJECTS_SETTING)


class Settings(Controller):

    class Meta:
        label = 'settings'
        stacked_type = 'nested'
        stacked_on = 'base'
        arguments = [
            (['-e', '--edit'], {
                'help': 'Edit the specified setting by passing the new values.',
                'action': 'store',
                'dest': 'new_value'
            })
        ]

    @ex(help='View or edit the list of ignored projects')
    def ignored_projects(self):
        setting = self.setting(IGNORED_PROJECTS_SETTING, self.app.pargs.new_value)
        self.app.render(setting)

    @ex(help='View or edit the omitt project name prefix')
    def omitt_prefix(self):
        setting = self.setting(OMITT_PREFIX_SETTING, self.app.pargs.new_value)
        self.app.render(setting)

    def setting(self, setting_name, new_value=None) -> dict:
        '''Gets or sets the setting specified by name.'''
        Setting = Query()
        setting = self.app.db.search(Setting.name == setting_name)
        # editing or inserting a setting value
        if new_value is not None:
            if not setting:
                self.app.db.insert({'name': setting_name, 'value': new_value})
            else:
                self.app.db.update({'value': new_value}, Setting.name == setting_name)
            return self.app.db.search(Setting.name == setting_name)
        # retrieving the setting value
        else:
            if not setting:
                self.app.log.info('Setting has not been set. You can configure it using -e')
            else:
                return self.app.db.search(Setting.name == setting_name)
