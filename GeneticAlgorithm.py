import csv

from src.Country import Country

# Total Cases, Infection Rate,

class Trainer:
    def __init__(self):
        self.countries = {}

        with open('src\\data\\train.csv', newline='') as file:
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

        with open('src\\data\\us_census.csv', newline='') as file:
            reader = csv.DictReader(file, delimiter=',', quotechar='"')

            for row in reader:
                if row['NAME'] in self.countries['US'].regions:
                    self.countries['US'].regions[row['NAME']].population = row['POPESTIMATE2019']

    def predict(self, country_name, region):
        country = self.countries[country_name]
        current = country.regions[region].get_current_cases()
        infection_rate = country.regions[region].get_infection_rate()
        population = country.regions[region].population
        print(current, infection_rate, population)
        
        next_day = current * infection_rate * (1 - c2 * current / population) * testing_factor


if __name__ == '__main__':
    trainer = Trainer()

    trainer.predict('US', 'Minnesota')
