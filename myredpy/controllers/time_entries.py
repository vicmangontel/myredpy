from datetime import date, datetime, timedelta
from cement import Controller, ex


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
        user = self.app.redmine.user.get('current')
        if user is None:
            raise ValueError('Current user could not be found.')

        if self.app.pargs.period is not None:
            period = self.app.pargs.period
            if period == 'day':
                self.get_entries_by_day(user.id)
            if period == 'week':
                self.get_entries_by_week(user.id, date.today(), self.app.pargs.show_weekends)
            if period == 'last-week':
                last_week_date = date.today() - timedelta(days=7)
                self.get_entries_by_week(user.id, last_week_date, self.app.pargs.show_weekends)
            if period == 'bi-week':
                print('bi-week')
            if period == 'month':
                print('month')
        else:
            self.get_entries_by_day(user.id)

    @ex(help='display time entry summary by period')
    def summary(self):
        self.app.render('summary')

    def get_entries_by_day(self, user_id):
        data = []
        for p in self.get_projects():
            entries = self.get_time_entries(user_id, p.id, date.today(), date.today())
            data.append([p.id, p.name, sum(x.hours for x in entries)])
        # add totals row at the bottom
        total_hours = sum(x[2] for x in data)
        data.append(['***', 'Total', total_hours])
        # render table
        self.app.render(data, headers=['id', 'project', 'hours'])

        if total_hours == 8:
            self.app.log.info('All the hours for today has been entered')

        if total_hours > 8:
            self.app.log.warning('You have logged more than 8 hours today.')

    def get_entries_by_week(self, user_id, week_date=date.today(), show_weekends=False):
        print(datetime.now().strftime('%c'))
        monday = week_date - timedelta(days=week_date.weekday())
        # move to the previouse week if last-week options was sent.
        days_to_show = 5
        if show_weekends is not None and show_weekends is not False:
            days_to_show = 7

        data = []
        headers = ['project']
        for p in self.get_projects():
            entries = self.get_time_entries(user_id, p.id, monday, monday + timedelta(days=5))
            days_to_check = range(0, days_to_show)
            entry_per_day = []
            day = monday
            for d in days_to_check:
                entry_per_day.append(sum(e.hours for e in filter(lambda x: x.spent_on == day, entries)))
                headers.append('{}'.format(day.strftime('%a-%d.%m')))
                day = day + timedelta(days=1)

            project_entry = [self.get_text(p.name)]
            project_entry.extend(entry_per_day)
            data.append(project_entry)

        # result = [sum(x) for x in zip(*data)]
        total_entry = ['Total']
        totals = [sum([row[i] for row in data]) for i in range(1, len(data[0]))]
        total_entry.extend(totals)
        data.append(total_entry)
        # main table -  tablefmt="grid"
        self.app.render(data, headers=headers)
        self.app.log.info('Period Total Spent Time: {}'.format(sum(x for x in totals)))

    def get_projects(self):
        active_projects = self.app.redmine.project.all().filter(status=1)
        ignored_projects = self.app.config.get('myredpy', 'ignored_projects').split(',')
        ignored_projects = list(map(int, ignored_projects))
        result = []
        for p in active_projects:
            if p.id in ignored_projects:
                continue
            result.append(p)
        return result

    def get_time_entries(self, user_id, project_id, from_date, to_date):
        return self.app.redmine.time_entry.filter(user_id=user_id, project_id=project_id, from_date=from_date, to_date=to_date)

    def get_text(self, text):
        # todo: replace this with a setting
        text = text.replace('Axos Bank - ', '')
        return (text[: 40] + '..') if len(text) > 42 else text
