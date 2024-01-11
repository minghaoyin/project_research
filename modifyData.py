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

from utils import *

p = {
    'l_x': 0, 'l_y': 1, 'l_p': 2, 'r_x': 3, 'r_y': 4, 'r_p': 5, 'v': 6, 't': 7,
    'l_var': 8, 'l_p_var': 9, 'l_r_diff': 10, 'cord': 11, 'floating': 12
}

o = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6
}

t = []

#l_var<1585 ->fixation
#def main(q_number):
#    g_data = open(f'data{q_number}.json', 'r')
def main(q, prefix):
    g_data=open(f'./{q}/ver1/{prefix}/data.json','r')
    gaze = json.load(g_data)

    g_data.close()

    start_time = gaze[0]['t']
    end_time = gaze[-1]['t']

    # gaze データフレーム
    g = []
    for i in range(len(gaze)):
        if not (gaze[i - 1]['t'] == gaze[i]['t']):
            cord = [
                    (float(gaze[i]['l_g'][0]) + float(gaze[i]['r_g'][0])) / 2,
                    (float(gaze[i]['l_g'][1]) + float(gaze[i]['r_g'][1])) / 2,
                ]
            
            cord
            g.append([
                gaze[i]['l_g'][0], gaze[i]['l_g'][1], gaze[i]['l_p'],
                gaze[i]['r_g'][0], gaze[i]['r_g'][1], gaze[i]['r_p'],
                all(gaze[i]['v']), round(gaze[i]['t'] - start_time, 3),
                None, None, None, cord, None
            ])

    # 線形補完
    # last_i = 0
    # is_gap = True
    # for i in range(len(g)):
    #     if not g[i][p['v']] and not is_gap:
    #         is_gap = True
    #         last_i = i - 1
    #     elif g[i][p['v']] and is_gap:
    #         is_gap = False

    #         time_diff = g[i][p['t']] - g[last_i][p['t']]
    #         if time_diff < 0.075 and not last_i == 0:
    #             diffs = []
    #             for j in range(6):
    #                 diffs.append(g[i][j] - g[last_i][j])
    #             for j in range(last_i + 1, i):
    #                 for k in range(6):
    #                     if g[j][k] == 'NaN':
    #                         g[j][k] = g[last_i][k] + diffs[k] * ((g[j][p['t']] - g[last_i][p['t']]) / time_diff)
    #                 g[j][p['v']] = True

    # 有効なデータのみ抽出

    l_p_var_tmp = []
    for i in range(1, len(g)):
        time_diff_before = g[i][p['t']] - g[i - 1][p['t']]

        # 視線移動量の算出
        if 0 < time_diff_before < 0.032:
            g[i][p['l_var']] = np.sqrt(((g[i][p['l_x']] - g[i - 1][p['l_x']]) * 1920) ** 2 +
                                       ((g[i][p['l_y']] - g[i - 1][p['l_y']]) * 1080) ** 2) / time_diff_before
            g[i][p['floating']]= 'floating' if(g[i][p['l_var']]>1585) else 'fixed'

        # 瞳孔拡張速度の算出
        if 0 < time_diff_before < 0.032:
            l_p_var = abs((g[i][p['l_p']] - g[i - 1][p['l_p']]) / time_diff_before)
            g[i][p['l_p_var']] = l_p_var
            l_p_var_tmp.append(l_p_var)

        # 左右瞳孔差の算出
        g[i][p['l_r_diff']] = abs(g[i][p['l_p']] - g[i][p['r_p']]) / min(g[i][p['l_p']], g[i][p['r_p']])

    # p_var_mad = np.median(np.abs((l_p_var_tmp - np.median(l_p_var_tmp))))
    # p_var_threshold = np.median(l_p_var_tmp) + 10 * p_var_mad

    l_p_var_tmp = np.array(l_p_var_tmp)
    quartile_1, quartile_3 = np.percentile(l_p_var_tmp, [25, 75])
    iqr = quartile_3 - quartile_1
    l_p_var_upper_bound = quartile_3 + (iqr * 1.5)

    g_l_p = np.array(g,dtype=object)[:, p['l_p']]
    quartile_1, quartile_3 = np.percentile(g_l_p, [25, 75])
    iqr = quartile_3 - quartile_1
    g_l_p_lower_bound = quartile_1 - (iqr * 1.5)
    g_l_p_upper_bound = quartile_3 + (iqr * 1.5)

    g_l_r_diff = np.array(g,dtype=object)[:, p['l_r_diff']]
    g_l_r_diff = list(filter(lambda x: x, g_l_r_diff))
    quartile_1, quartile_3 = np.percentile(g_l_r_diff, [25, 75])
    iqr = quartile_3 - quartile_1
    g_l_r_diff_upper_bound = quartile_3 + (iqr * 1.5)

    for i in range(1, len(g)):
        if g[i][p['t']] - g[i - 1][p['t']] > 0.075:
            # 空白に隣接するデータを削除
            for j in range(-3, 4):
                if 0 <= i + j < len(g) and abs(g[i + j][p['t']] - g[i][p['t']]) < 0.05:
                    g[i + j][p['v']] = False

        # 異常な瞳孔拡張速度を排除
        if g[i][p['l_p_var']] and l_p_var_upper_bound < g[i][p['l_p_var']]:
            g[i][p['v']] = False

        # 異常な瞳孔の大きさを削除
        if g[i][p['l_p']] < g_l_p_lower_bound or g_l_p_upper_bound < g[i][p['l_p']]:
            g[i][p['v']] = False

        # 異常な左右瞳孔差を削除
        if g[i][p['l_r_diff']] and g_l_r_diff_upper_bound < g[i][p['l_r_diff']]:
            g[i][p['v']] = False0

        # 固定な視線データのみ
        if g[i][p['floating']] == 'floating':
             g[i][p['v']] = False
        # 繰り返しデータ無くす
        if g[i][p['v']] == True:
            if g[i][p['t']] in t:
                g[i][p['v']] = False
            else:
                t.append(g[i][p['t']])
    # g = list(filter(lambda x: x[p['v']], g))x
    #
    # for row in g:
    #     if row[p['l_r_diff']] and row[p['l_r_diff']] > 0.3:
    #         print(row[p['l_r_diff']])

    # return list(filter(lambda x: x[p['v']], g))
    return g


#for q_number in range(1,2):
#        arr = main(q_number)
#        with open(f'/modifiedGaze/data{q_number}.json', 'w') as g:
#            g.write(json.dumps(arr))
for q in range(1,6):
    for key in o.keys():
        with open(f'./{q}/ver1/{key}/real2.json', 'w') as g:
            try:
                arr=[]
                arr=main(q, key)
                g.write(json.dumps(arr))
                print("saved")
            except:
                raise