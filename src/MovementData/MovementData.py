import json

from src.MovementData.State import State


class MovementData:
    def __init__(self):

        self.states = {}

        with open('../data/data.json', 'r') as file:
            data = file.read()
            raw = json.loads(data)

            for entry in raw:
                if entry['state'] == 'US':
                    if not entry['county'] in self.states:
                        self.states[entry['county']] = State(entry['county'])

                    if not entry['category'] in self.states[entry['county']].categories:
                        self.states[entry['county']].categories[entry['category']] = {}

                    self.states[entry['county']].categories[entry['category']][entry['date']] = {
                        "page": entry['page'],
                        "change": entry['change'],
                        "changecalc": entry['changecalc'],
                        'value': entry['value']
                    }

        for value in self.states['Alabama'].categories['parks']:
            print(value)


if __name__ == '__main__':
    movement = MovementData()
