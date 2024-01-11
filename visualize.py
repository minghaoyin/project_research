import json
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from PIL import Image
import itertools
import imageio
import gc

from utils import *



o = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6
}
n=0
x=[]
y=[]
for q in range(1,6):
    for key in o.keys():
        x=[]
        y=[]
        cor=[]
        existing_figures_before = len(plt.get_fignums())
        g_data=open(f'./{q}/ver1/{key}/real2.json','r')
        plt.close("all")
        plt.clf()
        #plt.gca().clear()
        #plt.gcf().clear()
        #gc.collect(2)
        #existing_figures_after = len(plt.get_fignums())
        plt.figure()
        gaze = json.load(g_data)
        image = plt.imread(f"{key}.png")
        plt.imshow(image)
        #pts = np.array([[330,620],[950,620],[692,450],[587,450]])
        #plt.plot(640, 570, "og", markersize=10)  # og:shorthand for green circle
        #plt.scatter(pts[:, 0], pts[:, 1], marker="x", color="red", s=200)
        #print(gaze)
        for i in range(len(gaze)):  
            try:
                #plt.plot(gaze[i]['l_g'][0],gaze[i]['l_g'][1])
                #break
                if(gaze[i][6] ==False):
                    continue
                #print(gaze[i][11][0])
                #print(gaze[i][11])
                x.append(gaze[i][11][0]*2239)
                y.append(gaze[i][11][1]*1400)
                cor.append(gaze[i][11])
                #print(gaze[i]['l_g'][0]+", "+gaze[i]['l_g'][1])
            except:
                raise
        #print(cor)
        #plt.scatter(cor_np[:, 0]*2239, cor_np[:, 1]*1400, marker="o", color="red", s=10)
        for i in np.arange(0,len(x),2):
            plt.plot(x[i:i+2],y[i:i+2],'k-')
        plt.plot(x[0],y[0],marker="x",color="black")
        plt.plot(x,y, marker=".")
        #plt.show()
        plt.savefig(f"./output/fig_{q}_{o[key]}.png")
        plt.close("all")
        plt.clf()
        n=n+1
        #existing_figures_after = len(plt.get_fignums())
        #print(f"Iteration {q}, Figures before: {existing_figures_before}, Figures after: {existing_figures_after}")


print(f"{n} success.")