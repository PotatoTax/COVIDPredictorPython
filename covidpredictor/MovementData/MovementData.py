import json
from pathlib import Path

from covidpredictor.MovementData.State import State


class MovementData:
    def __init__(self):

        self.states = {}

        resources = Path("resources")
        file_path = resources / "data.json"

        with open(file_path) as file:
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


if __name__ == '__main__':
    movement = MovementData()
