import math

import multiprocessing
from datetime import date

from DataGenerator import DataGenerator
from Pool import Pool


def parse_day(date_string):
    initial_date = date(2020, 1, 1).toordinal()

    split = [int(a) for a in date_string.split('-')]

    return date(split[0], split[1], split[2]).toordinal() - initial_date


class Trainer:
    def __init__(self, pool_size, start_training, country, region=None, covid_data=None, statistic='Cases'):
        # The object containing all case, fatality, and movement data
        self.covid_data = covid_data
        if covid_data is None:
            self.covid_data = DataGenerator()

        # The country and possibly specific region to generate a model for
        self.country = country
        self.region = region

        # The number of models for each generation
        self.pool_size = pool_size
        # What metric to create a model for, either 'Cases' or 'Fatalities'
        self.statistic = statistic

        # The date when training takes data from through 2 weeks later
        self.start_training = start_training

        # The object which handles all the models in a generation
        self.pool = Pool(pool_size)

        # The actual data which the predictions will be compared to
        self.test_case = []

        self.generate_test_case()

    def generate_test_case(self):
        # Gathers the case data for a week after the training data ends
        day_one = parse_day(self.start_training)
        if self.region is None:
            self.test_case = [self.country.daily[day_one + i][self.statistic] for i in range(7)]
        else:
            self.test_case = [self.region.daily[day_one + i][self.statistic] for i in range(7)]

    def train(self, generations):
        self.pool.seed_pool()

        # evaluates and creates a new generation
        for i in range(generations):
            self.threaded_evaluate()

            if i < generations - 1:
                self.pool.next_generation()

        # Returns the top 10 models
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
        prediction = self.predict(model, self.start_training)
        if self.region is None:
            model.score = self.rmsle(
                prediction,
                self.country.cumulative[parse_day(self.start_training)][self.statistic]
            )
        else:
            model.score = self.rmsle(
                prediction,
                self.region.cumulative[parse_day(self.start_training)][self.statistic]
            )
        return model

    def rmsle(self, predicted, baseline):
        # Root mean square log error test
        les = []

        predicted_cumulative = baseline
        actual_cumulative = baseline

        for predict, actual in zip(predicted, self.test_case):
            if predict < 0: predict = 0
            if actual < 0: actual = 0
            predicted_cumulative += predict
            actual_cumulative += actual

            les.append((math.log(predicted_cumulative + 1.0) - math.log(actual_cumulative + 1.0)) ** 2)

        return math.sqrt(sum(les) / len(les))

    def evaluate(self, start_date):
        # generates a week of predicted values for each model
        for model in self.pool.pool:
            model_predictions = self.predict(model, start_date)
            cumulative_stat = self.region.cumulative[parse_day(self.start_training)][self.statistic]
            model.score = self.rmsle(model_predictions, cumulative_stat)

    def predict(self, model, start_date):
        int_date = parse_day(start_date)

        if self.region is None:
            zone = self.country
        else:
            zone = self.region

        previous_cases = zone.daily[int_date][self.statistic]

        lag = model.mobility_lag

        week_prediction = []
        if self.statistic == 'Cases':
            for day in range(7):
                mobility_stats = []
                for category in zone.categories.values():
                    movement_stat = []
                    for date in range(int_date + day - lag - 4, int_date + day - lag + 1):
                        try:
                            movement_stat.append(category[date]['value'])
                        except:
                            continue
                    mobility_stats.append(sum(movement_stat) / len(movement_stat))
                prediction = model.predict(previous_cases, mobility_stats, zone.infection_rate(), zone.population)
                week_prediction.append(prediction)
                previous_cases = prediction
        else:
            for day in range(7):
                week_ago_cases = 0
                for i in range(int_date - 8 + day, int_date - 5 + day):
                    week_ago_cases += zone.daily[i]['Cases']
                prediction = int(model.fatality_ratio * week_ago_cases / 3)
                week_prediction.append(prediction)

        return week_prediction


if __name__ == '__main__':
    predictions = {}
    scores = []
    covid_data = DataGenerator()

    for country in [covid_data.country("US")]:
        print(country.name)
        for region in country.regions.values():
            print("\t" + region.name)
            # if region in ["Guam", "Virgin Islands", "Puerto Rico"]:
            #     continue
            trainer = Trainer(10000, "2020-03-30", country, region, covid_data, 'Fatalities')

            top_models = trainer.train(1)

            for model in top_models[:1]:
                # print(f"Fatality ratio : {region.fatality_ratio()}")
                print("\t", trainer.predict(model, "2020-03-30"), model.score)
                print()
                scores.append(model.score)

    print(f"\nAverage score over {len(scores)} regions : {sum(scores) / len(scores)}")

    # Illinois, New Mexico, Oregon, Tennessee, Utah, New Hampshire, Missouri, Maine, Kentucky, Colorado
