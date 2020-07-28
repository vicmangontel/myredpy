from tinydb import Query
from cement import Controller, ex
from myredpy.core.constants import (OMITT_PREFIX_SETTING, IGNORED_PROJECTS_SETTING)


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

    @ex(help='View or edit the project alias',
        arguments=[
            (['-p', '--project_id'],
             {'help': 'The project to add or edit the alias',
              'action': 'store',
              'dest': 'project_id'})
        ])
    def project_alias(self):
        table = self.app.db.table('project_alias')
        project_id = self.app.pargs.project_id
        # if no project_id was given, retrieve all current alias
        if not project_id:
            data = []
            for p in table.all():
                data.append([p['project_id'], p['alias']])
            self.app.render(data, headers=['project_id', 'alias'])
            return

        try:
            new_value = self.app.pargs.new_value
            document = None
            Alias = Query()
            if new_value:
                document = table.search(Alias.project_id == project_id)
                if document:
                    table.update({'alias': new_value}, Alias.project_id == project_id)
                else:
                    table.insert({'project_id': project_id, 'alias': new_value})
            else:
                document = table.search(Alias.project_id == project_id)[0]
                self.app.render(document)
        except IndexError:
            self.app.log.info('No records found')
        except:
            self.app.log.error('There was an error while loading the data.')

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
        if not setting:
            self.app.log.info('Setting has not been set. You can configure it using -e')
        else:
            return self.app.db.search(Setting.name == setting_name)
