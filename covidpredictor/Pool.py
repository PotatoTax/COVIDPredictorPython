class Pool:
    def __init__(self, size):
        self.size = size

        self.pool = []

    def seed_pool(self):
        for _ in range(self.size):
            self.pool.append(Model())