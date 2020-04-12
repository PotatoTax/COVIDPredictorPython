import random


class Model:

    def __init__(self, list_mob_constants, c_immunity, mobility_lag):
        self.mobility_constants = list_mob_constants
        self.immunity_constant = c_immunity
        self.mobility_lag = mobility_lag
        self.score = 10000

        self.immunity_variability = .05
        self.mobility_lag_variability = [-1, 1]
        self.mobility_constant_variability = .1

    @classmethod
    def random(cls):
        mobility_constants = [random.uniform(-1, 1) for _ in range(6)]
        immunity_constant = random.random() * 10
        lag = random.randint(5, 25)

        return Model(mobility_constants, immunity_constant, lag)

    def mutate(self):
        new_c_immunity = random.gauss(1, self.immunity_variability) * self.immunity_constant
        new_mobility_lag = self.mobility_lag + random.randint(self.mobility_lag_variability[0], self.mobility_lag_variability[1])
        if new_mobility_lag < 7:
            new_mobility_lag = 7
        new_mobility_constants = []
        for constant in self.mobility_constants:
            new_mobility_constants.append(random.gauss(1, self.mobility_constant_variability) * constant)

        return Model(new_mobility_constants, new_c_immunity, new_mobility_lag)

    def predict(self, current, mobility, infection_rate, population):
        testing_factor = 1
        mobility_factor = 0

        for i in range(len(mobility)):
            mobility_factor += self.mobility_constants[i] * mobility[i]

        immunity_factor = 1 - self.immunity_constant * (current / population)

        prediction = current * infection_rate * mobility_factor * immunity_factor * testing_factor

        if prediction < 0:
            return 0
        return int(prediction)
