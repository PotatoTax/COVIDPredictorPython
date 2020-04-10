from datetime import date

from covidpredictor.CaseData.Region import Region


class Country(Region):
    initial_date = date(2020, 1, 1).toordinal()

    def __init__(self, name):
        super().__init__(name)

        self.regions = {}

        self.cumulative = {}
        self.daily = {}

    def add_day(self, date_string, values):
        day = self.parse_day(date_string)

        if day in self.cumulative:
            self.cumulative[day]['Cases'] += values['Cases']
            self.cumulative[day]['Fatalities'] += values['Fatalities']
        else:
            self.cumulative[day] = {
                'Cases': values['Cases'],
                'Fatalities': values['Fatalities']
            }

        if not values['Region'] == '':
            if values['Region'] in self.regions:
                self.regions[values['Region']].add_day(day, values)
            else:
                self.regions[values['Region']] = Region(values['Region'])

    def calculate_daily(self):
        for day in self.cumulative.keys():
            if day > 22:
                self.daily[day] = {
                    'Cases': self.cumulative[day]['Cases'] - self.cumulative[day - 1]['Cases'],
                    'Fatalities': self.cumulative[day]['Fatalities'] - self.cumulative[day - 1]['Fatalities']
                }

    def parse_day(self, date_string):
        split = [int(a) for a in date_string.split('-')]

        return date(split[0], split[1], split[2]).toordinal() - self.initial_date
