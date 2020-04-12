from random import gauss, randint


class Model:
    def __init__(self, list_mob_constants, c_immunity, mobility_lag):
        self.mobility_constants = list_mob_constants
        self.immunity_constant = c_immunity
        self.mobility_lag = mobility_lag

    def mutate(self):
        new_c_immunity = gauss(1, 0.05)*self.immunity_constant
        new_mobility_lag = self.mobility_lag + randint(-1, 1)
        if new_mobility_lag < 7:
            new_mobility_lag = 7
        new_list_mob_constants = []
        for constant in self.mobility_constants:
            new_list_mob_constants.append(gauss(1, 0.001)*constant)

        return Model(new_list_mob_constants, new_c_immunity, new_mobility_lag)

    def predict(self, current, mobility, infection_rate, population):
        testing_factor = 1
        mobility_factor = 0

        for i in range(len(mobility)):
            mobility_factor += self.mobility_constants[i] * mobility[i]

        immunity_factor = 1 - self.immunity_constant * (current / population)

        return int(current * infection_rate * mobility_factor * immunity_factor * testing_factor)
