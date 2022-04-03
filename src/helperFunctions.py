import json
with open("./data/defaultValues",'r') as f:
    vars = json.load(f)
for var in vars['variables'][0]:
    globals()[var] = vars['variables'][0][var]