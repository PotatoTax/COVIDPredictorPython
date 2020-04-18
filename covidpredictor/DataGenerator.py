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
        files = glob.glob("resources/mobilityData/*.json")

        for file_path in files:
            with open(file_path) as file:
                data = file.read()
                raw = json.loads(data)

                for entry in raw:
                    if not entry["country"] in self.countries:
                        self.countries[entry["country"]] = Country(entry["country"])

                    self.countries[entry["country"]].add_movement(entry)

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
        census_data = Path("resources/population")
        # US States
        file_path = census_data / "us_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                if row["NAME"] in self.countries['US'].regions:
                    self.countries['US'].regions[row["NAME"]].population = int(row['POPESTIMATE2019'])

        file_path = census_data / "us_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                if row["Province"] in self.countries['US'].regions:
                    self.countries['US'].regions[row["Province"]].population = int(row['Population'])

        # Global National Data
        file_path = census_data / "world_population_2018.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                if row["Name"] in self.countries:
                    self.countries[row["Name"]].population = int(row["Population"])

        # Australian States
        file_path = census_data / "australia_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row[""].replace(";", "").split("   ")[2].strip()

                self.country("Australia").region(name).population = int(row["Sep-2019"])

        # Canadian Provinces
        file_path = census_data / "canada_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row[""]

                self.country("Canada").region(name).population = int(row["Persons"])

        # Chinese Provinces
        file_path = census_data / "china_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row["Province"].replace("Municipality", "").replace("Autonomous Region", "").strip()

                self.country("China").region(name).population = int(row["Population"])

        # Denmark Provinces
        file_path = census_data / "denmark_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row["Province"]

                self.country("Denmark").region(name).population = int(row["Population"])

        # French Provinces
        file_path = census_data / "france_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row["Province"]

                self.country("France").region(name).population = int(row["Population"])

        # UK Provinces
        file_path = census_data / "uk_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row["Province"]

                self.country("United Kingdom").region(name).population = int(row["Population"])

        # Netherlands Provinces
        file_path = census_data / "netherlands_regional_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                name = row["Province"]

                self.country("Netherlands").region(name).population = int(row["Population"])

    def country(self, country):
        return self.countries[country]


if __name__ == '__main__':
    move = DataGenerator()
