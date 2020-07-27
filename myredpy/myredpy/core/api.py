from tinydb import Query
from redminelib import Redmine
from .constants import (IGNORED_PROJECTS_SETTING)

class Api(object):
    """
    Redmine Resouse Api abstraction. 
    """

    def __init__(self, app):
        self._redmine = app.redmine
        self._db = app.db
        self._log = app.log
    
    def projects(self, include_ignored_projects=False, use_alias=True):
        '''Returns the active projects for the current user'''
        result = []
        ignored_projects = self.ignored_projects() if not include_ignored_projects else []
        
        for p in self._redmine.project.all().filter(status=1):
            if not include_ignored_projects and p.id in ignored_projects:
                continue
            if use_alias:
                alias = self.project_alias(p.id)
                p.name = alias if alias else p.name
            result.append(p)
        
        return result
    
    def ignored_projects(self) -> []:
        '''Returns the list of ignored project ids stored in the configuration settings'''
        try:
            setting = self._db.search(Query().name == IGNORED_PROJECTS_SETTING)
            if setting:
                id_list = setting[0].get('value').split(',')
                return [int(d) for d in id_list] if id_list else []
            return []
        except Exception as e:
            self._app._log.error(str(e), __name__)
            return []

    def project_alias(self, project_id:int) -> str:
        '''Returns the alias for the specified project from the configuration settings'''
        table = self._db.table('project_alias')
        aliases = table.search(Query().project_id == str(project_id))
        if aliases:
            return aliases[0]['alias']
        return None