import json
import os
import random
import sys

if len(sys.argv) < 4:
    print ("Please pass the number of items, maximum weight, maximum item weight,\nand maximum item cost as parameter.")
    print ("Usage:")
    print ("CreateProblemData <# items> <max weight> <max item weight> <max item cost>")
else:
    numberOfItems = int(sys.argv[1])
    maximumWeight = int(sys.argv[2])
    maximumItemWeight = int(sys.argv[3])
    maximumItemCost = int(sys.argv[4])

    items = []
    for i in range(numberOfItems):
        items.append({ "id": i, "weight": random.randint(1, maximumItemWeight), "cost": random.randint(1,maximumItemCost)})

    pData = { "weight": maximumWeight, "items": items }
    pProblem = { "type": "knapsack", "data": pData }

    print(json.dumps(pProblem))
