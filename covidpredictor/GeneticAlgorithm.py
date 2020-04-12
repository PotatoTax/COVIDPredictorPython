from tqdm import tqdm
from numpy import *
from datetime import date

from CaseData.CaseData import CaseData
from Model import Model
from MovementData.MovementData import MovementData


def rsmle(predicted, actual):
    les = []
    for index in range(len(predicted)):
        les.append(log(predicted[index] + 1) - log(actual[index] + 1))
    return sqrt(sum(les)/len(les))


def iterate(current, mobility_stats, infection_rate, population, model):
    c_immunity = model.immunity_constant
    list_mob_constants = model.mobility_constants
    testing_factor = 1
    mobility_factor = 0
    for i in range(len(mobility_stats)):
        mobility_factor += list_mob_constants[i]*mobility_stats[i]
    immunity_factor = 1 - c_immunity * (current/population)

    return int(current * infection_rate * mobility_factor * immunity_factor * testing_factor)


class Trainer:
    def __init__(self, pool_size):
        self.pool_size = pool_size

        self.case_data = CaseData()

        self.pool = []

    def generate_pool(self):
        self.pool = []

        for _ in range(self.pool_size):
            generated_mobility_constants = [random.random() for _ in range(6)]
            generated_immunity_constants = random.random()
            generated_lag = random.randint(5,15)
            model = Model(generated_mobility_constants, generated_immunity_constants, generated_lag)
            self.pool.append(model)

    def next_generation(self, scores):
        # sort pool based on scores
        self.pool = [x for _, x in sorted(zip(scores, self.pool))]
        # TODO : fix population size variability
        reproduce_pool = []
        for index in range(len(self.pool)):
            if random.randint(1, len(self.pool)) < index:
                reproduce_pool.append(self.pool[index])

        self.pool = []
        for working_model in reproduce_pool:
            self.pool.append(working_model)
            self.pool.append(working_model.mutate())

    def evaluate(self, start_date):
        # generate scores for each model
        predictions = []

        for model in self.pool:
            model_predictions = []
            for state in self.case_data.get_country('US').regions:
                print(state)
                if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                    continue
                model_predictions.extend(self.predict('US', state, model, start_date))
            predictions.append(model_predictions)

        results = []
        for state in self.case_data.get_country('US').regions:
            print(state)
            if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                continue
            region = self.case_data.get_country('US').regions[state]
            week_pred = []
            for i in range(7):
                week_pred.append(region.cumulative[region.parse_day(start_date) + i]['Cases'])
            results.extend(week_pred)

        scores = []
        for index in range(len(predictions)):
            scores.append(rsmle(predictions[index], results))

        return scores

    def train(self, generations):
        self.generate_pool()

        # TODO : Implement multiprocessing
        for _ in tqdm(range(generations)):
            scores = self.evaluate("2020-03-30")
            self.next_generation(scores)
            print(len(self.pool))

        final_scores = self.evaluate("2020-03-30")
        sorted_final_pool = [x for _, x in sorted(zip(final_scores, self.pool))]

        return sorted_final_pool[0]

    def predict(self, country_name, region, model, start_date):
        country = self.case_data.get_country(country_name)
        current = country.regions[region].get_current_cases()
        infection_rate = country.regions[region].get_infection_rate()
        population = int(country.regions[region].population)

        testing_factor = 1

        one_week_prediction = []
        prev = current

        int_date = country.regions[region].parse_day(start_date)
        lag = model.mobility_lag

        movement_data = MovementData()

        for day in range(7):
            mobility_stats = []
            for category in movement_data.states[region].categories.values():
                movement_stat = []
                for date in range(int_date + day - lag - 4, int_date + day - lag + 1):
                    try:
                        movement_stat.append(category[date]['value'])
                    except:
                        continue
                mobility_stats.append(sum(movement_stat) / len(movement_stat))
            new_day = iterate(prev, mobility_stats, infection_rate, population, model)
            one_week_prediction.append(new_day)
            prev = new_day

        return one_week_prediction


if __name__ == '__main__':
    trainer = Trainer(1000)

    model = trainer.train(20)

    print(trainer.predict('US', 'Minnesota', model))
    print(model.mobility_constants, model.immunity_constant)
