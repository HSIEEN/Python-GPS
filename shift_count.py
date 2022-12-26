# Data : 12/22/2022 5:46 PM
# Author: Shawn Shi
# Right Reserved By COROS
import numpy as np

def shift_evaluate(std, track):
    Cs = np.average(std, axis=0)
    Ct = np.average(track, axis=0)
    # standard track center
    area = 0.0
    Csx, Csy = 0.0, 0.0
    for i in range(len(std)):
        x = std[i][0]
        y = std[i][1]
        if i == len(std)-1:
            x1 = std[0][0]
            y1 = std[0][1]
        else:
            x1 = std[i+1][0]
            y1 = std[i+1][1]
        tri = ((x*y1-x1*y)+(x1*Cs[1]-Cs[0]*y1)+(Cs[0]*y-x*Cs[1]))/2.0
        area = area + tri
        Csx = Csx + tri*(x+x1+Cs[0])/3.0
        Csy = Csy + tri*(y+y1+Cs[1])/3.0
    Csx = Csx/area
    Csy = Csy/area
    # test track center
    area = 0.0
    Ctx, Cty = 0.0, 0.0
    for i in range(len(track)):
        x = track[i][0]
        y = track[i][1]
        if i == len(track)-1:
            x1 = track[0][0]
            y1 = track[0][1]
        else:
            x1 = track[i+1][0]
            y1 = track[i+1][1]
        tri = ((x*y1-x1*y)+(x1*Ct[1]-Ct[0]*y1)+(Ct[0]*y-x*Ct[1]))/2.0
        area = area + tri
        Ctx = Ctx + tri*(x+x1+Ct[0])/3.0
        Cty = Cty + tri*(y+y1+Ct[1])/3.0
    Ctx = Ctx/area
    Cty = Cty/area
    shift = [Csx-Ctx, Csy-Cty]

    return shift
