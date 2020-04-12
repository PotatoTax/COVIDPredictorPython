import math

from tqdm import tqdm
import multiprocessing

from CaseData.CaseData import CaseData
from MovementData.MovementData import MovementData
from Pool import Pool


class Trainer:
    def __init__(self, pool_size):
        self.pool_size = pool_size

        self.case_data = CaseData()

        self.movement_data = MovementData()

        self.pool = Pool(pool_size)

        self.test_case = []

        self.generate_test_case()

    def generate_test_case(self):
        for state in self.case_data.get_country('US').regions:
            if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                continue
            region = self.case_data.get_country('US').regions[state]
            day_one = region.parse_day("2020-03-30")
            week_pred = [region.daily[day_one + i]['Cases'] for i in range(7)]
            self.test_case.extend(week_pred)

    def train(self, generations):
        self.pool.seed_pool()

        for i in tqdm(range(generations)):
            self.threaded_evaluate()

            if i < generations - 1:
                self.pool.next_generation()

        self.pool.sort()

        return self.pool.pool[:10]

    def threaded_evaluate(self):
        # a thread_count of 4 seems to be the most effective
        # higher values slow the program
        thread_count = 4

        with multiprocessing.Pool(thread_count) as worker_pool:
            result = worker_pool.map(self.thread, self.pool.pool)

            # waits for all the processes to finish and closes them
            worker_pool.close()
            worker_pool.join()

            # replaces the pool with the new models
            self.pool.pool = result

    def thread(self, model):
        predictions = []
        for state in self.case_data.get_country('US').regions:
            if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
                continue
            predictions.extend(self.predict('US', state, model, start_date="2020-03-30"))

        model.score = self.rmsle(predictions)
        return model

    def rmsle(self, predicted):
        les = []

        for predict, actual in zip(predicted, self.test_case):
            if actual < 0: actual = 0
            try:
                les.append((math.log(predict + 1.0) - math.log(actual + 1.0)) ** 2)
            except ValueError:
                print(predict, actual)

        return math.sqrt(sum(les) / len(les))

    def evaluate(self, start_date):
        # generates a week of predicted values for each model
        for model in self.pool.pool:
            model_predictions = []
            for state in self.case_data.get_country('US').regions:
                if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                    continue
                model_predictions.extend(self.predict('US', state, model, start_date))

            model.score = self.rmsle(model_predictions)

    def predict(self, country_name, region, model, start_date):
        country = self.case_data.get_country(country_name)
        current = country.regions[region].get_daily_cases()
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
    trainer = Trainer(10000)

    top_models = trainer.train(1)

    for model in top_models:
        print(trainer.predict('US', 'Minnesota', model, "2020-03-30"), model.score)
        print(model.mobility_constants, model.immunity_constant)
        print(model.mobility_lag)
        print()
