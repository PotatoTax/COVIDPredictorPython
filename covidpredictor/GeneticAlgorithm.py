from tqdm import tqdm
from numpy import *
import multiprocessing

from CaseData.CaseData import CaseData
from Model import Model
from MovementData.MovementData import MovementData


class Trainer:
    def __init__(self, pool_size):
        self.pool_size = pool_size

        self.case_data = CaseData()

        self.movement_data = MovementData()

        self.pool = []

        self.test_case = []

        self.generate_test_case()

    def generate_test_case(self):
        for state in self.case_data.get_country('US').regions:
            if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                continue
            region = self.case_data.get_country('US').regions[state]
            week_pred = []
            for i in range(7):
                week_pred.append(region.cumulative[region.parse_day("2020-03-30") + i]['Cases'])
            self.test_case.extend(week_pred)

    def generate_pool(self):
        self.pool = []

        for _ in range(self.pool_size):
            generated_mobility_constants = [random.random() for _ in range(6)]
            generated_immunity_constants = random.random()
            generated_lag = random.randint(5,15)
            model = Model(generated_mobility_constants, generated_immunity_constants, generated_lag)
            self.pool.append(model)

    def rsmle(self, predicted):
        les = []
        for index in range(len(predicted)):
            les.append(log(predicted[index] + 1.0) - log(self.test_case[index] + 1.0))
        return sqrt(sum(les) / len(les))

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
        predictions = []
        scores = []

        # generates a week of predicted values for each model
        for model in self.pool:
            model_predictions = []
            for state in self.case_data.get_country('US').regions:
                if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                    continue
                model_predictions.extend(self.predict('US', state, model, start_date))
            predictions.append(model_predictions)

            scores.append(self.rsmle(model_predictions))

        return scores

    def train(self, generations):
        self.generate_pool()

        # TODO : Implement multiprocessing
        for _ in tqdm(range(generations)):
            scores = self.evaluate("2020-03-30")
            self.next_generation(scores)

        final_scores = self.evaluate("2020-03-30")
        sorted_final_pool = [x for _, x in sorted(zip(final_scores, self.pool))]

        return sorted_final_pool[0]

    def predict(self, country_name, region, model, start_date):
        country = self.case_data.get_country(country_name)
        current = country.regions[region].get_current_cases()
        infection_rate = country.regions[region].get_infection_rate()
        population = int(country.regions[region].population)


        previous_cases = current

        int_date = country.regions[region].parse_day(start_date)
        lag = model.mobility_lag

        week_prediction = []
        for day in range(7):
            mobility_stats = []
            for category in self.movement_data.states[region].categories.values():
                movement_stat = []
                for date in range(int_date + day - lag - 4, int_date + day - lag + 1):
                    try:
                        movement_stat.append(category[date]['value'])
                    except:
                        continue
                mobility_stats.append(sum(movement_stat) / len(movement_stat))
            prediction = model.predict(previous_cases, mobility_stats, infection_rate, population)
            week_prediction.append(prediction)
            previous_cases = prediction

        return week_prediction


if __name__ == '__main__':
    trainer = Trainer(1000)

    model = trainer.train(20)

    print(trainer.predict('US', 'Minnesota', model, "2020-03-30"))
    print(model.mobility_constants, model.immunity_constant)
    print(model.mobility_lag)
