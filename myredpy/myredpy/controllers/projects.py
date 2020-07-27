from cement import Controller, ex

class Projects(Controller):
    class Meta:
        label = 'projects'
        stacked_type = 'nested'
        stacked_on = 'base'
    
    def _default(self):
        """Default action if no sub-command is passed"""
        data = []
        for project in self.app.redmine.project.all().filter(status = 1):
            data.append([project.id, project.name, project.status])
        
        self.app.render(data, headers=['id', 'name', 'status'], tablefmt='fancy_grid')

    @ex(
        help='gets the specified project details',
        arguments=[(['project_id'], { 'help': 'project identifier', 'action': 'store'}),],
    )
    def detail(self):
        try:
            project = self.app.redmine.project.all().get(int(self.app.pargs.project_id), None)

            if project is None:
                self.app.log.warning('No project found with id {}'.format(id))
                return

            filter_fields = ['id', 'name', 'identifier', 'status', 'created_on']
            data = [(x, y) for (x, y) in list(project) if x in filter_fields]

            self.app.render(data, headers=['field', 'value'], tablefmt='fancy_grid')
        except TypeError as err:
            self.app.log.error('Cannot retrieve project: {}'.format(err))
