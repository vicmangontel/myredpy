import calendar
from datetime import date, datetime, timedelta
from tinydb import Query
from cement import Controller, ex
from myredpy.core.formatters import to_multiline_text
from myredpy.core.settings_name import (OMITT_PREFIX_SETTING, IGNORED_PROJECTS_SETTING)
from myredpy.core.api import Api


class TimeEntries(Controller):
    class Meta:
        label = 'time-entries'
        stacked_type = 'nested'
        stacked_on = 'base'

        arguments = [
            (['-sw', '--show-weekends'],
             {
                'help': 'specify if weekends will be shown',
                'action': 'store_true',
                'dest': 'show_weekends'
            })
        ]

    @ex(help='Todays entries grouped by project')
    def today(self):
        projects = self.app.api.projects()

        if len(projects) == 0:
            self.app.log.info('Projects were not found...')
            return
        # table to hold the data to display + total row
        data = []
        total_hours = 0
        for p in projects:
            project_hours = sum(x.hours for x in self.time_entries(self.user_id(), p.id))
            data.append([p.id, p.name, project_hours])
            total_hours += project_hours
        # add totals row at the bottom
        data.append(['', 'TOTAL', total_hours])
        # render table
        print(datetime.now().strftime('%c'))
        self.app.render(data, headers=['id', 'project', 'hours'], tablefmt='fancy_grid')
        self.display_daily_summary(total_hours)

    @ex(
        help='Weekly entries grouped by project. Can display last week entries',
        arguments=[(['-l', '--last-week'], {
            'help': 'specify if last week time entries should be displayed instead of current week ones',
            'action': 'store_true',
            'dest': 'display_last_week'
        })]
    )
    def week(self, show_weekends=False):
        week_date = date.today()
        if self.app.pargs.display_last_week:
            week_date = date.today() - timedelta(days=7)
        # define the start of the week
        monday = week_date - timedelta(days=week_date.weekday())
        # move to the previous week if last-week options was sent.
        days_to_show = 5
        if show_weekends is not None and show_weekends is not False:
            days_to_show = 7

        data = []
        headers = ['project']
        prefix_to_omitt = self.setting(OMITT_PREFIX_SETTING)

        for p in self.app.api.projects():
            entries = self.time_entries(self.user_id(), p.id, monday, monday + timedelta(days=5))
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

    @ex(help='Fortnight (15 days) entries for current period. I.e. 1-15 or 16-31')
    def fortnight(self):
        today = date.today()
        date_range = (today, today)
        total_days = 15
        # check if it is first or second month fortnight and adjust the date range
        if today.day < 16:
            date_range = (date(today.year, today.month, 1), date(today.year, today.month, 15))
        else:
            last_day = calendar.monthrange(today.year, today.month)[1]
            total_days = last_day - 15
            date_range = (date(today.year, today.month, 16), date(today.year, today.month, last_day))

        projects = self.app.api.projects()
        # retrieve and calculate time entries
        data = self.time_entries_by_date_range(projects, date_range, total_days)
        self.app.render(data, headers="firstrow", tablefmt='fancy_grid')

    @ex(help='Monthly entries for current period')
    def month(self):
        today = date.today()
        total_days = calendar.monthrange(today.year, today.month)[1]
        date_range = (date(today.year, today.month, 1), date(today.year, today.month, total_days))
        data = self.time_entries_by_date_range(api.projects(), date_range, total_days)
        self.app.render(data, headers="firstrow", tablefmt='fancy_grid')

    def time_entries_by_date_range(self, projects, date_range, total_days):
        w, h = (len(projects) + 2), (total_days + 2)
        data = [[0 for x in range(w)] for y in range(h)]
        data[0][0] = 'C|_|'
        data[0][len(projects)+1] = 'Sum'
        data[total_days+1][0] = 'Total'

        current_project = 1
        #total_hours_in_period = 0
        for p in projects:
            day = date_range[0]
            entries = self.time_entries(self.user_id(), p.id, date_range[0], date_range[1])
            total_hours_by_project = 0
           # set project name as header
            data[0][current_project] = p.name
            # get and sum time entries
            for i in range(1, total_days+1):
                data[i][0] = day.strftime('%a-%d.%m')
                if day.weekday() > 4 and not self.app.pargs.show_weekends:
                    data[i][current_project] = '***'
                else:
                    data[i][current_project] = sum(e.hours for e in filter(lambda x: x.spent_on == day, entries))
                    total_hours_by_project += data[i][current_project]
                # sum current row totals per day
                if isinstance(data[i][current_project], str):
                    data[i][len(projects)+1] = '***'
                else:
                    data[i][len(projects)+1] += data[i][current_project]
                # advance to next day calculations
                day = day + timedelta(days=1)
            # print sumary
            data[total_days+1][current_project] = total_hours_by_project
            #total_hours_in_period += total_hours_by_project
            data[total_days+1][len(projects)+1] += total_hours_by_project
            # advance to the next project
            current_project += 1
        # return result
        return data

    def user_id(self) -> int:
        '''Returns the current user id (defined by the Redmine API Key)'''
        user = self.app.redmine.user.get('current')
        if user is None:
            raise ValueError('Current user could not be found.')
        return user.id

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
