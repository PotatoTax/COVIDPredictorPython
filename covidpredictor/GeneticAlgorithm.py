import math

from tqdm import tqdm
import multiprocessing
from datetime import date

from CaseData import Region
from CaseData.CaseData import CaseData
from MovementData.MovementData import MovementData
from Pool import Pool


class Trainer:
    def __init__(self, pool_size, state=None, statistic='Cases'):
        self.state = state

        self.pool_size = pool_size

        self.statistic = statistic

        self.case_data = CaseData()

        self.movement_data = MovementData()

        self.pool = Pool(pool_size)

        self.test_case = []

        self.generate_test_case()

    def generate_test_case(self):
        # Gathers the case data for a week after the training data ends
        day_one = self.parse_day("2020-03-30")
        if self.state is None:
            for state in self.case_data.get_country('US').regions:
                if state == "Guam" or state == "Virgin Islands" or state == "Puerto Rico":
                    continue
                region = self.case_data.get_country('US').regions[state]
                week_pred = [region.daily[day_one + i][self.statistic] for i in range(7)]
                self.test_case.extend(week_pred)
        else:
            region = self.case_data.get_country('US').regions[self.state]
            self.test_case = [region.daily[day_one + i][self.statistic] for i in range(7)]

    def train(self, generations):
        self.pool.seed_pool()

        # evaluates and creates a new generation
        for i in tqdm(range(generations)):
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
        predictions = []
        if self.state is None:
            for state in self.case_data.get_country('US').regions:
                if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
                    continue
                predictions.extend(self.predict('US', state, model, start_date="2020-03-30"))
        else:
            predictions = self.predict('US', self.state, model, start_date="2020-03-30")
        model.score = self.rmsle(predictions, self.case_data.get_country('US').regions[self.state].cumulative[self.parse_day("2020-03-30")][self.statistic])
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

    def evaluate(self, start_date):
        # generates a week of predicted values for each model
        for model in self.pool.pool:
            model_predictions = []
            if self.state is None:
                for state in self.case_data.get_country('US').regions:
                    if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
                        continue
                    model_predictions.extend(self.predict('US', state, model, start_date))
            else:
                model_predictions = self.predict('US', self.state, model, start_date)
            cumulative_stat = self.case_data.get_country('US').regions[self.state].cumulative[self.parse_day("2020-03-30")][self.statistic]
            model.score = self.rmsle(model_predictions, cumulative_stat)

    def predict(self, country_name, region, model, start_date):
        country = self.case_data.get_country(country_name)
        previous_cases = country.regions[region].daily[self.parse_day(start_date)][self.statistic]
        infection_rate = country.regions[region].get_infection_rate()
        fatality_ratio = country.regions[region].get_fatality_ratio()
        population = int(country.regions[region].population)

        int_date = self.parse_day(start_date)
        lag = model.mobility_lag

        week_prediction = []
        if self.statistic == 'Cases':
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
        else:
            for day in range(7):
                week_ago_cases = 0
                for i in range(self.parse_day(start_date) - 8 + day, self.parse_day(start_date) - 5 + day):
                    week_ago_cases += country.regions[region].daily[i]['Cases']
                prediction = int(fatality_ratio * week_ago_cases / 3)
                week_prediction.append(prediction)

        return week_prediction

    def parse_day(self, date_string):
        initial_date = date(2020, 1, 1).toordinal()

        split = [int(a) for a in date_string.split('-')]

        return date(split[0], split[1], split[2]).toordinal() - initial_date

if __name__ == '__main__':

    '''scores = []
    for state in CaseData().get_country('US').regions.keys():
        if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
            continue
        trainer = Trainer(10000, state, 'Cases')

        top_models = trainer.train(1)

        for model in top_models[:1]:
            print(state)
            print(trainer.predict('US', state, model, "2020-03-30"), model.score)
            scores.append(model.score)

    print(sum(scores) / len(scores))'''

    scores = []
    for state in CaseData().get_country('US').regions.keys():
        if state in ["Guam", "Virgin Islands", "Puerto Rico"]:
            continue
        trainer = Trainer(10000, state, 'Fatalities')

        top_models = trainer.train(1)

        for model in top_models[:1]:
            print(state)
            print("Fatality ratio to cases 7 days prior:", CaseData().get_country('US').regions[state].get_fatality_ratio())
            print(trainer.predict('US', state, model, "2020-03-30"), model.score)
            scores.append(model.score)

    print(sum(scores) / len(scores))

    # Illinois, New Mexico, Oregon, Tennessee, Utah, New Hampshire, Missouri, Maine, Kentucky, Colorado