from random import gauss, randint


class Model:
    def __init__(self, list_mob_constants, c_immunity, mobility_lag):
        self.mobility_constants = list_mob_constants
        self.immunity_constant = c_immunity
        self.mobility_lag = mobility_lag

    def mutate(self):
        new_c_immunity = gauss(1, 0.05)*self.immunity_constant
        new_mobility_lag = self.mobility_lag + random.randint(-1, 1)
        new_list_mob_constants = []
        for constant in self.mobility_constants:
            new_list_mob_constants.append(gauss(1, 0.001)*constant)

        return Model(new_list_mob_constants, new_c_immunity, new_mobility_lag)
