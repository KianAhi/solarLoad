import os
import yaml

class House:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__),"../data/defaultValues.yaml" ), 'r') as stream:
            index = "config"
            try:
                load = yaml.safe_load(stream)
                for key in load[index]:
                    setattr(self, key, load[index][key])
            except yaml.YAMLError as exc:
                print(exc)