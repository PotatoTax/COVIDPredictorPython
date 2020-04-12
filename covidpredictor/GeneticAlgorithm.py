from tqdm import tqdm
from numpy import *
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
            week_pred = [region.cumulative[day_one + i]['Cases'] for i in range(7)]
            self.test_case.extend(week_pred)

    def train(self, generations):
        self.pool.seed_pool()

        for _ in tqdm(range(generations)):
            self.threaded_evaluate()
            self.pool.next_generation()

        self.evaluate("2020-03-30")
        self.pool.sort()

        return self.pool.pool[0]

    def threaded_evaluate(self):
        # a thread_count of 4 seems to be the most effective
        # higher values slow the program
        thread_count = 4

        if thread_count == 1:
            # if there is only one thread, don't bother creating a process
            self.thread(self.case_data, self.pool.pool)
        else:
            # splits the pool into equal sized jobs
            job_size = len(self.pool.pool) // thread_count

            jobs = []
            for i in range(thread_count):
                jobs.append(self.pool.pool[job_size * i: job_size * (i + 1)])

            threads = []
            for job in jobs:
                thread = multiprocessing.Process(target=self.thread, args=(self.case_data, job,))
                threads.append(thread)

            for t in threads:
                t.start()

            for t in threads:
                t.join()

    def thread(self, case_data, models):
        for model in models:
            predictions = []
            for state in case_data.get_country('US').regions:
                if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
                    continue
                predictions.extend(self.predict('US', state, model, start_date="2020-03-30"))

            model.score = self.rmsle(predictions)

    def rmsle(self, predicted):
        les = []

        # return sqrt(mean_squared_log_error(self.test_case, predicted))

        for index in range(len(predicted)):
            les.append((log(predicted[index] + 1.0) - log(self.test_case[index] + 1.0)) ** 2)

        return sqrt(sum(les) / len(les))

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

    model = trainer.train(10)

    print(trainer.predict('US', 'Minnesota', model, "2020-03-30"))
    print(model.mobility_constants, model.immunity_constant)
    print(model.mobility_lag)
