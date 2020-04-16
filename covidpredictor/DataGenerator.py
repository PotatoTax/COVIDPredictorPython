import csv
import glob
import json
from datetime import date
from pathlib import Path

from Country import Country

initial_date = date(2020, 1, 1).toordinal()

resources = Path("resources")


class DataGenerator:
    def __init__(self):
        self.countries = {}

        self.movement_data()
        self.case_date()
        self.population_data()

    def movement_data(self):
        files = glob.glob("data/data/*.json")

        for file_path in files:
            with open(file_path) as file:
                data = file.read()
                raw = json.loads(data)

                for entry in raw:
                    if not entry["country"] in self.countries:
                        self.countries[entry["country"]] = Country(entry["country"])

                    self.countries[entry["country"]].add_entry(entry)

    def case_date(self):
        file_path = resources / "train.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                entry = {
                    "Region": row["Province_State"],
                    "Cases": float(row["ConfirmedCases"]),
                    "Fatalities": float(row["Fatalities"])
                }

                if (row['Country_Region']) in self.countries:
                    self.countries[row['Country_Region']].add_cases(row['Date'], entry)
                else:
                    self.countries[row['Country_Region']] = Country(row['Country_Region'])
                    self.countries[row['Country_Region']].add_cases(row['Date'], entry)

    def population_data(self):

        # US States
        file_path = resources / "us_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                if row["NAME"] in self.countries['US'].regions:
                    self.countries['US'].regions[row["NAME"]].population = int(row['POPESTIMATE2019'])

        # Global National Data
        file_path = resources / "world_population_2018.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                if row["Name"] in self.countries:
                    self.countries[row["Name"]].population = int(row["Population"])

        # Australian States
        file_path = resources / "australia_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row[""].replace(";", "").split("   ")[2].strip()

                self.country("Australia").region(name).population = int(row["Sep-2019"])

        # Canadian Provinces
        file_path = resources / "canada_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row[""]

                try:
                    self.country("Canada").region(name).population = int(row["Persons"])
                except KeyError:
                    print(f"Region \"{name}\" not in dataset")

    def country(self, country):
        return self.countries[country]


if __name__ == '__main__':
    move = DataGenerator()
