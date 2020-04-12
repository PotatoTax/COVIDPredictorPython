from datetime import date


class Region:
    initial_date = date(2020, 1, 1).toordinal()

    def __init__(self, name):
        self.name = name

        self.cumulative = {}
        self.daily = {}

    def add_day(self, day, values):
        self.cumulative[day] = {
            'Cases': values['Cases'],
            'Fatalities': values['Fatalities']
        }

        if day > 22:
            self.daily[day] = {
                'Cases': values['Cases'] - self.cumulative[day - 1]['Cases'],
                'Fatalities': values['Fatalities'] - self.cumulative[day - 1]['Fatalities']
            }
        else:
            self.daily[day] = {
                'Cases': values['Cases'],
                'Fatalities': values['Fatalities']
            }

    def get_current_cases(self):
        day = max(self.cumulative.keys())

        return self.cumulative[day]['Cases']

    def get_daily_cases(self):
        day = max(self.daily.keys())

        return self.daily[day]['Cases']

    def get_infection_rate(self):
        start_date = -1

        for day in self.cumulative.keys():
            if self.cumulative[day]['Cases'] > 0:
                start_date = day
                break

        total = 0

        for i in range(start_date + 10, start_date + 20):
            if i in self.cumulative.keys():
                total += self.cumulative[i]['Cases'] / self.cumulative[i - 1]['Cases']

        return total / 10

    def parse_day(self, date_string):
        split = [int(a) for a in date_string.split('-')]

        return date(split[0], split[1], split[2]).toordinal() - self.initial_date
