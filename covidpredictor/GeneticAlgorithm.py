import math

from tqdm import tqdm
import multiprocessing
from datetime import date

from DataGenerator import DataGenerator
from Pool import Pool


def parse_day(date_string):
    initial_date = date(2020, 1, 1).toordinal()

    split = [int(a) for a in date_string.split('-')]

    return date(split[0], split[1], split[2]).toordinal() - initial_date


class Trainer:
    def __init__(self, pool_size, start_date, state=None, covid_data=None, statistic='Cases'):
        self.state = state

        self.pool_size = pool_size

        self.statistic = statistic

        self.start_date = start_date

        self.covid_data = covid_data
        if covid_data is None:
            self.covid_data = DataGenerator()

        self.pool = Pool(pool_size)

        self.test_case = []

        self.generate_test_case()

    def generate_test_case(self):
        # Gathers the case data for a week after the training data ends
        day_one = parse_day(self.start_date)
        if self.state is None:
            for state in self.covid_data.get_country('US').regions:
                if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                    continue
                region = self.covid_data.get_country('US').regions[state]
                week_pred = [region.daily[day_one + i][self.statistic] for i in range(7)]
                self.test_case.extend(week_pred)
        else:
            region = self.covid_data.get_country('US').regions[self.state]
            self.test_case = [region.daily[day_one + i][self.statistic] for i in range(7)]

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
        int_date = parse_day(self.start_date)

        predictions = []
        if self.state is None:
            for state in self.covid_data.get_country('US').regions:
                if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
                    continue
                predictions.extend(self.predict_trainer('US', state, model, self.start_date))
        else:
            predictions = self.predict_trainer('US', self.state, model, self.start_date)
        model.score = self.rmsle(predictions, self.covid_data.get_country('US').regions[self.state].cumulative[
                int_date][self.statistic])
        return model

    def rmsle(self, predicted, baseline):
        # Root mean square log error test
        les = []

        predicted_cumulative = baseline
        actual_cumulative = baseline

        for predict, actual in zip(predicted, self.test_case):
            if actual < 0: actual = 0
            predicted_cumulative += predict
            actual_cumulative += actual
            les.append((math.log(predicted_cumulative + 1.0) - math.log(actual_cumulative + 1.0)) ** 2)

        return math.sqrt(sum(les) / len(les))

    def evaluate(self):
        # generates a week of predicted values for each model
        int_date = parse_day(self.start_date)

        for model in self.pool.pool:
            model_predictions = []
            if self.state is None:
                for region in self.covid_data.get_country('US').regions:
                    if region in ["Guam", "Virgin Islands", "Puerto Rico"]:
                        continue
                    model_predictions.extend(self.predict_trainer('US', region, model, self.start_date))
            else:
                model_predictions = self.predict_trainer('US', self.state, model, self.start_date)
            cumulative_stat = self.covid_data.get_country('US').regions[self.state].cumulative[int_date][self.statistic]
            model.score = self.rmsle(model_predictions, cumulative_stat)

    def predict_trainer(self, country_name, region, model, start_date):
        int_date = parse_day(start_date)

        country = self.covid_data.get_country(country_name)
        region = country.get_region(region)
        previous_cases = region.daily[int_date][self.statistic]
        infection_rate = region.get_infection_rate()
        population = int(region.population)

        lag = model.mobility_lag

        week_prediction = []
        if self.statistic == 'Cases':
            for day in range(7):
                mobility_stats = []
                for category in region.categories.values():
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
        else:
            for day in range(7):
                week_ago_cases = 0
                for i in range(int_date - 8 + day, int_date - 5 + day):
                    week_ago_cases += region.daily[i]['Cases']
                prediction = int(model.fatality_ratio * week_ago_cases / 3)
                week_prediction.append(prediction)

        return week_prediction

    def predict_day(self, country_name, region, model, int_date):
        country = self.covid_data.get_country(country_name)
        region = country.get_region(region)

        if self.statistic == 'Cases':
            print('uhhh, no bueno')

        else:
            week_ago_cases = 0
            for i in range(int_date - 8, int_date - 5):
                week_ago_cases += region.daily[i]['Cases']
            prediction = int(model.fatality_ratio * week_ago_cases / 3)

        return prediction

if __name__ == '__main__':

    '''scores = []
    for state in CaseData().get_country('US').regions.keys():
        if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
            continue
        trainer = Trainer(10000, state, 'Cases')

        top_models = trainer.train(1)

        for model in top_models[:1]:
            print(state)
            print(trainer.predict_trainer('US', state, model, "2020-03-30"), model.score)
            scores.append(model.score)

    print(sum(scores) / len(scores))'''

    scores = []
    covid_data = DataGenerator()
    for state in covid_data.get_country('US').regions:
        trainer = Trainer(1000, "2020-03-30", state, covid_data, 'Fatalities')

        top_models = trainer.train(1)

        for model in top_models[:1]:
            print(state)
            print(f"Fatality ratio : {model.fatality_ratio}")
            print(trainer.predict_trainer('US', state, model, "2020-03-30"), model.score)
            print()
            scores.append(model.score)

            # Write to regional daily dict
            last_day = max(covid_data.get_country('US').regions[state].daily.keys())
            for i in range(6):
                day = last_day + i + 1
                covid_data.get_country('US').regions[state].daily[day] = {'Cases': None, 'Fatalities': trainer.predict_day('US', state, model, day)}

    print(f"\nAverage score over {len(scores)} regions : {sum(scores) / len(scores)}")

    # Illinois, New Mexico, Oregon, Tennessee, Utah, New Hampshire, Missouri, Maine, Kentucky, Colorado
