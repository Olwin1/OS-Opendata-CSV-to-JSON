import json
import os
import numpy as np
places = []

createdFiles = os.listdir("./JSON/")
for file in createdFiles:
    data = json.load(open(f"./JSON/{file}"))
    places = np.concatenate([places, data])
    print(f"File {file} added")
with open('output.json', 'w') as fp:
    json.dump(places.tolist(), fp)