import math
from datetime import date

from Region import Region


class Country(Region):
    initial_date = date(2020, 1, 1).toordinal()

    def __init__(self, name):
        super().__init__(name)

        self.regions = {}

        self.cumulative = {}
        self.daily = {}

    def add_cases(self, date_string, values):
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
                self.regions[values['Region']].add_cases(day, values)
            else:
                self.regions[values['Region']] = Region(values['Region'])

    def add_movement(self, entry):
        if "region" in entry and not entry["region"] is None:
            if entry["region"] in self.regions:
                self.regions[entry["region"]].add_movement(entry)
        else:
            if not entry["category"] in self.categories:
                self.categories[entry["category"]] = {}

            self.categories[entry["category"]][self.parse_day(entry["date"])] = {
                "change": entry["change"],
                "changecalc": entry["changecalc"],
                "value": sig(float(entry["value"]) / 100)
            }

    def calculate_daily(self):
        for day in self.cumulative.keys():
            if day > 22:
                self.daily[day] = {
                    'Cases': self.cumulative[day]['Cases'] - self.cumulative[day - 1]['Cases'],
                    'Fatalities': self.cumulative[day]['Fatalities'] - self.cumulative[day - 1]['Fatalities']
                }

    def region(self, region):
        return self.regions[region]

    def parse_day(self, date_string):
        split = [int(a) for a in date_string.split('-')]

        return date(split[0], split[1], split[2]).toordinal() - self.initial_date


def sig(x):
    return .4 / (1 + math.e ** (-.33 * x)) + .8
