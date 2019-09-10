from tinydb import Query
from cement import Controller, ex


class Settings(Controller):
    class Meta:
        label = 'settings'
        stacked_type = 'nested'
        stacked_on = 'base'
        arguments = [
            (['-e', '--edit'], {
                'help': 'Edit the specified setting by passing the new values.',
                'action': 'store',
                'dest': 'newValue'
            })
        ]

    @ex(help='View or edit the list of ignored projects')
    def ignored_projects(self):
        SETTING_NAME = 'ignored_projects'
        Setting = Query()
        setting = self.app.db.search(Setting.name == SETTING_NAME)

        newValue = self.app.pargs.newValue
        if newValue is not None:
            if setting is None or len(setting) == 0:
                self.app.db.insert({'name': SETTING_NAME, 'value': newValue})
            else:
                self.app.db.update({'value': newValue}, Setting.name == SETTING_NAME)
        else:
            if setting is None or len(setting) == 0:
                self.app.log.info('Setting has not been set. You can configure it using -e')
            else:
                self.app.render(setting)
