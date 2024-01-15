import json
import pandas as pd
import numpy as np
import os
import seaborn as sns
from scipy import stats
from PIL import Image
import itertools


o = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6
}
n=0
result = []

for q in range(1,6):
  for key in o.keys():
    g_data = open(f'./{q}/ver1/{key}/real2.json','r')
    data = json.load(g_data)
    
    prevCoord = [0, 0]
    first = True
    distance_sum = 0
    count = 0
    start_time = 0
    end_time = 0
    true_count = 0
    false_count = 0

    for d in data[1:]:
      if d[6] == True:
        if first:
          first = False
          start_time = d[7]
        else:
          distance_sum += np.sqrt((d[0] - prevCoord[0])**2 + (d[1] - prevCoord[1])**2)
          end_time = d[7]
          true_count += 1
        
        prevCoord = d[0:2]
      else:
        if not(first):
          false_count += 1
    
    result.append([q, o[key], distance_sum, (end_time - start_time), true_count, false_count])
  result.append([])


# csvファイルに書き出し
df = pd.DataFrame(result)
df.to_csv('result.csv', index=False)

