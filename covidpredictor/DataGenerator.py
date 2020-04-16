import csv
import glob
import json
from datetime import date
from pathlib import Path

from Country import Country

initial_date = date(2020, 1, 1).toordinal()


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
        file_path = Path("CaseData") / "train.csv"

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
        file_path = Path("CaseData") / "us_census.csv"

        with open(file_path) as file:
            reader = csv.DictReader(file, delimiter=",", quotechar='"')

            for row in reader:
                if row["NAME"] in self.countries['US'].regions:
                    self.countries['US'].regions[row["NAME"]].population = row['POPESTIMATE2019']

    def get_country(self, country):
        return self.countries[country]
