from myredpy.core.api import Api
from cement import Controller, ex


class Issues(Controller):

    class Meta:
        label = 'issues'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(
        help='All issues assigned to current user (excluding filteres projects unless specified)',
        arguments=[(['-a', '--all'], {
            'help': 'includes all issues unfiltered',
            'action': 'store_true',
            'dest': 'all'
        })]
    )
    def all(self):
        raise NotImplementedError
        # user = self.app.redmine.user.get('current')
        # if not user:
        #     raise ValueError('Current user is not found. Redmine API Key might be missing from configuration.')
        # project_api = ProjectApi(self.app)
        # self.app.render(project_api.projects())
