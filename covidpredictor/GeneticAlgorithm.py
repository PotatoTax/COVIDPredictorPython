import csv

from covidpredictor.MovementData.MovementData import MovementData
from covidpredictor.CaseData.CaseData import CaseData


class Trainer:
    def __init__(self):
        self.case_data = CaseData()
        self.movement_data = MovementData()

        with open('resources/us_census.csv', newline='') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')

            for row in reader:
                if row['NAME'] in self.case_data.get_country('US').regions:
                    self.case_data.get_country('US').regions[row['NAME']].population = row['POPESTIMATE2019']

    def predict(self, country_name, region):
        country = self.case_data.get_country(country_name)
        current = country.regions[region].get_current_cases()
        infection_rate = country.regions[region].get_infection_rate()
        population = country.regions[region].population

        next_day = current * infection_rate

        print(next_day)


if __name__ == '__main__':
    trainer = Trainer()

    trainer.predict('US', 'Minnesota')
