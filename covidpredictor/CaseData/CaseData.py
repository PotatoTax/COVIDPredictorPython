import csv
from pathlib import Path

from covidpredictor.CaseData.Country import Country


class CaseData:
    def __init__(self):
        self.countries = {}

        resources = Path("CaseData//data")
        file_path = resources / "train.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')

            for row in reader:
                entry = {
                    'Region': row['Province_State'],
                    'Cases': float(row['ConfirmedCases']),
                    'Fatalities': float(row['Fatalities'])
                }

                if (row['Country_Region']) in self.countries:
                    self.countries[row['Country_Region']].add_day(row['Date'], entry)
                else:
                    self.countries[row['Country_Region']] = Country(row['Country_Region'])
                    self.countries[row['Country_Region']].add_day(row['Date'], entry)

        file_path = resources / "us_census.csv"

        with open(file_path, newline='') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')

            for row in reader:
                if row['NAME'] in self.countries['US'].regions:
                    self.countries['US'].regions[row['NAME']].population = row['POPESTIMATE2019']

    def get_country(self, country_name):
        return self.countries[country_name]


if __name__ == '__main__':
    d = CaseData()
    print(d.countries['US'].regions['New York'].get_infection_rate())
