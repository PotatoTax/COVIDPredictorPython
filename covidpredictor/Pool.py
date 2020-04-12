import random

from Model import Model


class Pool:
    def __init__(self, size):
        self.size = size

        self.pool = []

    def seed_pool(self):
        for _ in range(self.size):
            self.pool.append(Model.random())

    def next_generation(self):
        self.sort()

        reproduce_pool = []

        for i in range(len(self.pool)):
            if random.randint(1, len(self.pool)) < i:
                reproduce_pool.append(self.pool[i])

        self.pool = []
        for model in reproduce_pool:
            self.pool.append(model)
            self.pool.append(model.mutate())

    def sort(self):
        self.pool.sort(key=lambda x: x.score, reverse=False)
