import random


class Model:

    def __init__(self, list_mob_constants, c_immunity, mobility_lag, fatality_ratio):
        self.mobility_constants = list_mob_constants
        self.immunity_constant = c_immunity
        self.mobility_lag = mobility_lag
        self.score = 10000
        self.fatality_ratio = fatality_ratio

        self.immunity_variability = .05
        self.mobility_lag_variability = [-1, 1]
        self.mobility_constant_variability = .1
        self.fatality_variability = 0.01

    @classmethod
    def random(cls):
        mobility_constants = [random.uniform(-1, 1) for _ in range(6)]
        immunity_constant = random.random() * 10
        #lag = random.randint(5, 25)
        lag = 16
        fatality_ratio = random.random()/2

        return Model(mobility_constants, immunity_constant, lag, fatality_ratio)

    def mutate(self):
        new_c_immunity = random.gauss(1, self.immunity_variability) * self.immunity_constant
        new_fatality = random.gauss(1, self.fatality_variability)*self.fatality_ratio
        new_mobility_lag = self.mobility_lag + random.randint(self.mobility_lag_variability[0], self.mobility_lag_variability[1])
        if new_mobility_lag < 7:
            new_mobility_lag = 7
        new_mobility_constants = []
        for constant in self.mobility_constants:
            new_mobility_constants.append(random.gauss(1, self.mobility_constant_variability) * constant)

        return Model(new_mobility_constants, new_c_immunity, new_mobility_lag, new_fatality)

    def predict(self, current, mobility, infection_rate, population):
        testing_factor = 1
        mobility_factor = 0

        for i in range(len(mobility)):
            mobility_factor += self.mobility_constants[i] * mobility[i]

        immunity_factor = 1 - self.immunity_constant * (current / population)

        prediction = current * infection_rate * mobility_factor * immunity_factor * testing_factor

        # if prediction < 0:
        #     return 0
        return int(prediction)
