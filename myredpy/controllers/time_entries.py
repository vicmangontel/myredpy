from datetime import date, datetime, timedelta
from tinydb import Query
from cement import Controller, ex
from myredpy.core.formatters import to_multiline_text
from myredpy.core.settings_name import (OMITT_PREFIX_SETTING, IGNORED_PROJECTS_SETTING)


class TimeEntries(Controller):
    class Meta:
        label = 'time-entries'
        stacked_type = 'nested'
        stacked_on = 'base'

        arguments = [
            (['-p', '--period'],
             {
                'help': 'specify the period to show. Valid values: [day, week, last-week, bi-week, month]',
                'action': 'store',
                'dest': 'period'
            }),
            (['-sw', '--show-weekends'],
             {
                'help': 'specify if weekends will be shown',
                'action': 'store_true',
                'dest': 'show_weekends'
            })
        ]

    def _default(self):
        """Default action if no sub-command is passed."""
        try:
            user = self.app.redmine.user.get('current')
            if user is None:
                raise ValueError('Current user could not be found.')

            period = self.app.pargs.period
            if period is not None:
                if period == 'day':
                    self.today_entries(user.id)
                if period == 'week':
                    self.entries_by_week(user.id, date.today(), self.app.pargs.show_weekends)
                if period == 'last-week':
                    last_week_date = date.today() - timedelta(days=7)
                    self.entries_by_week(user.id, last_week_date, self.app.pargs.show_weekends)
                if period == 'bi-weekly':
                    print('bi-weekly')
                if period == 'month':
                    print('month')
            else:
                self.today_entries(user.id)
        except Exception as e:
            self.app.log.debug(repr(traceback.extract_stack()))
            self.app.log.error(str(e), __name__)

    def today_entries(self, user_id):
        projects = self.projects(self.ignored_projects())
        if len(projects) == 0:
            self.app.log.info('Projects were not found...')
            return
        # table to hold the data to display + total row
        data = []
        total_hours = 0
        for p in projects:
            project_hours = sum(x.hours for x in self.time_entries(user_id, p.id))
            data.append([p.id, p.name, project_hours])
            total_hours += project_hours
        # add totals row at the bottom
        data.append(['', 'TOTAL', total_hours])
        # render table
        print(datetime.now().strftime('%c'))
        self.app.render(data, headers=['id', 'project', 'hours'], tablefmt='fancy_grid')
        self.display_daily_summary(total_hours)

    def entries_by_week(self, user_id, week_date=date.today(), show_weekends=False):
        monday = week_date - timedelta(days=week_date.weekday())
        # move to the previous week if last-week options was sent.
        days_to_show = 5
        if show_weekends is not None and show_weekends is not False:
            days_to_show = 7

        data = []
        headers = ['project']
        prefix_to_omitt = self.setting(OMITT_PREFIX_SETTING)

        for p in self.projects(self.ignored_projects()):
            entries = self.time_entries(user_id, p.id, monday, monday + timedelta(days=5))
            days_to_check = range(0, days_to_show)
            entry_per_day = []
            day = monday
            for d in days_to_check:
                hours = sum(e.hours for e in filter(lambda x: x.spent_on == day, entries))
                entry_per_day.append(hours)
                headers.append('{}'.format(day.strftime('%a-%d.%m')))
                day = day + timedelta(days=1)

            project_entry = [to_multiline_text(p.name, omitt_prefix=prefix_to_omitt)]
            project_entry.extend(entry_per_day)
            data.append(project_entry)

        total_entry = ['TOTAL']
        totals = [sum([row[i] for row in data]) for i in range(1, len(data[0]))]
        total_entry.extend(totals)
        data.append(total_entry)
        # main table
        print(datetime.now().strftime('%c'))
        self.app.render(data, headers=headers, tablefmt='fancy_grid')
        self.app.log.info('Period Total Spent Time: {}'.format(sum(x for x in totals)))

    def ignored_projects(self) -> []:
        '''Returns the list of ignored projects configured by settings'''
        try:
            id_list = self.setting(IGNORED_PROJECTS_SETTING).split(',')
            return [int(d) for d in id_list] if id_list else []
        except Exception as e:
            self.app.log.error(str(e), __name__)
            return []

    def projects(self, ignored_projects=None):
        '''Returns active projects for the current User. Additionally a list of ignored projects can be passed.'''
        result = []
        for p in self.app.redmine.project.all().filter(status=1):
            if ignored_projects and p.id in ignored_projects:
                continue
            result.append(p)
        return result

    def time_entries(self, user_id, project_id, from_date=date.today(), to_date=date.today()):
        '''Returns the time entries filtered by user, project and date ranage'''
        return self.app.redmine.time_entry.filter(
            user_id=user_id, project_id=project_id, from_date=from_date, to_date=to_date
        )

    def display_daily_summary(self, hours: int) -> None:
        '''Logs info according to the logged hours by day'''
        if hours == 8:
            self.app.log.info('All the hours for today has been entered')

        if hours > 8:
            self.app.log.warning('You have logged more than 8 hours today.')

    def setting(self, setting_name: str) -> str:
        '''Returns the setting value from the local db given the setting name'''
        setting = self.app.db.search(Query().name == setting_name)
        if setting:
            return setting[0].get('value')
        return None
