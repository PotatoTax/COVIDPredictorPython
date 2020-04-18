import math
from datetime import date


class Region:
    initial_date = date(2020, 1, 1).toordinal()

    def __init__(self, name):
        self.name = name

        self.cumulative = {}
        self.daily = {}

        self.categories = {}

    def add_cases(self, day, values):
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

    def add_movement(self, entry):
        if not entry["category"] in self.categories:
            self.categories[entry["category"]] = {}

        self.categories[entry["category"]][self.parse_day(entry["date"])] = {
            "change": entry["change"],
            "changecalc": entry["changecalc"],
            "value": sig(float(entry["value"]) / 100)
        }

    def infection_rate(self):
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

    def fatality_ratio(self):
        start_date = -1

        for day in self.cumulative.keys():
            if self.cumulative[day]['Fatalities'] > 0:
                start_date = day + 7
                break

        total = 0
        length = max(self.cumulative.keys()) - start_date
        for i in range(start_date, max(self.cumulative.keys())):
            try:
                total += self.daily[i]['Fatalities'] / self.daily[i - 7]['Cases']
            except:
                length -= 1

        if length < 5:
            return 0.05

        return total/length

    def parse_day(self, date_string):
        split = [int(a) for a in date_string.split('-')]

        return date(split[0], split[1], split[2]).toordinal() - self.initial_date


def sig(x):
    return .4 / (1 + math.e ** (-.33 * x)) + .8

