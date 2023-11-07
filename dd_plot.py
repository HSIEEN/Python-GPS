# created by Shawn Shi at 2023/10/18
# all rights are reserved by COROS
# created by Shawn Shi at 2023/10/18
# all rights are reserved by COROS
import sys
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# 打开文件
root = tk.Tk()
root.withdraw()
filenames = \
    filedialog.askopenfilenames(filetypes=[('*.res', 'Res Files'), ('*.*', 'All Files')], title='选择res文件，可以多选')

# 检查用户是否选择了一个文件
if filenames == '' or filenames == '.':
    sys.exit('没有文件被选中，程序结束')
else:
    filenumber = -1
    # resdata: system/PRN/epoch
    resdata1 = np.array([[[[float('nan') for _ in range(1000)] for _ in range(64)]
                          for _ in range(6)] for _ in range(len(filenames))])
    resdata2 = np.array([[[[float('nan') for _ in range(1000)] for _ in range(64)]
                          for _ in range(6)] for _ in range(len(filenames))])
    # resflag: system/freq/PRN
    resflag = np.array([[[[0 for _ in range(64)] for _ in range(2)]
                         for _ in range(6)] for _ in range(len(filenames))])
    for filename in filenames:
        filenumber += 1
        with open(filename, 'r') as file:
            line = file.readline()
            data = []
            num = 0
            # azimuth and elevation, system/PRN/epoch
            # azi_data1 = np.array([[[float('nan') for _ in range(1000)] for _ in range(64)] for _ in range(6)])
            # azi_data2 = np.array([[[float('nan') for _ in range(1000)] for _ in range(64)] for _ in range(6)])
            # ele_data1 = np.array([[[float('nan') for _ in range(1000)] for _ in range(64)] for _ in range(6)])
            # ele_data2 = np.array([[[float('nan') for _ in range(1000)] for _ in range(64)] for _ in range(6)])

            # 逐行读取数据
            while line:
                data = line.split()
                if data[0] == '*':
                    num += 1
                    line = file.readline()
                    data = line.split()
                    while data[0] == '#':
                        isys = int(data[1])
                        freq = int(data[2])
                        nsat = int(data[3])
                        for _ in range(nsat):
                            line = file.readline()
                            data = line.split()
                            prn = int(data[1])
                            if isys == 5:
                                prn = prn - 192
                            snr = float(data[3])
                            res = float(data[2])
                            ele = float(data[5])
                            azi = float(data[6])
                            if freq == 0:
                                resdata1[filenumber][isys][prn][num] = res
                                # ele_data1[isys][prn][num] = ele
                                # azi_data1[isys][prn][num] = azi
                            else:
                                resdata2[filenumber][isys][prn][num] = res
                                # ele_data2[isys][prn][num] = ele
                                # azi_data2[isys][prn][num] = azi
                            resflag[filenumber][isys][freq][prn] = 1
                        line = file.readline()
                        if line:
                            data = line.split()
                line = file.readline()

# 画图
sysstr = ["GPS", "GLO", "BD2", "BD3", "Gal", "QZS"]
csys = ["G", "R", "C", "C", "E", "J"]
# flag = 1
# for i in range(6):
#     for j in range(2):
#         f = plt.figure(flag)
#         figure_ok = False
#         titlestr = sysstr[i] + ' - L' + str(1 if j == 0 else 5)
#         for k in range(64):
#             if resflag[i][j][k] == 1:
#                 if i == 5:
#                     prnstr = csys[i] + str(k + 192)
#                 else:
#                     prnstr = csys[i] + str(k)
#                 if j == 0:
#                     y = [resdata1[i][k][q] for q in range(num)]
#                 else:
#                     y = [resdata2[i][k][q] for q in range(num)]
#                 plt.plot(range(1, num + 1), y, '.', label=prnstr)
#                 plt.xlabel('Epoches')
#                 plt.ylabel('Residuals')
#                 plt.legend()
#                 plt.title(titlestr)
#                 plt.axis([0, num + 1, -100, 100])
#                 figure_ok = True
#         if figure_ok:
#             flag += 1
#         else:
#             plt.close(f)

# for i in range(6):
#     for j in range(2):
#         f = plt.figure(flag)
#         y = []
#         azi = []
#         ele = []
#         figure_ok = False
#         titlestr = sysstr[i] + ' - L' + str(1 if j == 0 else 5)
#         for k in range(64):
#             if resflag[i][j][k] == 1:
#                 if i == 5:
#                     prnstr = csys[i] + str(k + 192)
#                 else:
#                     prnstr = csys[i] + str(k)
#                 if j == 0:
#                     y.extend([abs(resdata1[i][k][q]) for q in range(num)])
#                     azi.extend([azi_data1[i][k][q]/180*np.pi for q in range(num)])
#                     ele.extend([ele_data1[i][k][q] for q in range(num)])
#                 else:
#                     y.extend([abs(resdata2[i][k][q]) for q in range(num)])
#                     azi.extend([azi_data2[i][k][q]/180*np.pi for q in range(num)])
#                     ele.extend([ele_data2[i][k][q] for q in range(num)])
#                 # plt.plot(range(1, num + 1), y, '.', label=prnstr)
#                 figure_ok = True
#         colors = y
#         ax = f.add_subplot(projection='polar')
#         ax.set_ylim(90, 0, 10)
#         # ax.set_theta_zero_location('W', offset=270)
#         ax.set_theta_zero_location("N")  # theta=0 at the top
#         ax.set_theta_direction(-1)  # theta increasing clockwise
#         norm = plt.Normalize(0, 10)
#         cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
#             "", ["green", "lime", "yellow", "gold", "orange", "red"])
#         # c = ax.scatter(azi, ele, c=colors, cmap=cmap, norm=norm)
#         plt.scatter(azi, ele, c=colors, cmap=cmap, norm=norm)
#         plt.colorbar()
#         plt.title(titlestr+' - Psudo-res')
#         # plt.axis([0, num + 1, -100, 100])
#         if figure_ok:
#             flag += 1
#         else:
#             plt.close(f)

mean_values = []
std_values = []
sat_freqs = []
for ii in range(len(filenames)):
    """# 计算平均值，标准差，RMSE"""
    mean_value = []
    std_value = []
    sat_freq = []
    for i in range(6):
        for j in range(2):
            y = []
            std_ok = False
            for k in range(64):
                if resflag[ii][i][j][k] == 1:
                    for q in range(num):
                        if j == 0:
                            value = resdata1[ii][i][k][q]
                        else:
                            value = resdata2[ii][i][k][q]
                        if not math.isnan(value):
                            y.append(value)
                            std_ok = True
            if std_ok:
                S = round(np.std(y), 3)
                M = round(np.mean(y), 3)
                R = np.sqrt(np.mean(np.square(y)))
                mean_value.append(abs(M))
                std_value.append(S)
                sat_freq.append(sysstr[i] + '-L' + str(1 if j == 0 else 5))
                print('file:', filenames[ii].split('/')[-1], 'System-Freq:',
                      sysstr[i] + '-L' + str(1 if j == 0 else 5), 'Ave:', round(M, 3),
                      'STD:', round(S, 3), 'RMS:', round(R, 3))
    mean_values.append(mean_value)
    std_values.append(std_value)
    sat_freqs.append(sat_freq)
"""plot bar with matplotlib"""
files = list([filenames[i].split('/')[-1].split('.')[0] for i in range(len(filenames))])
"""
create two dictionaries to store all means and stds respectively
"""
union_list = []
# for i in range(len(filenames)):
#     union_list += sat_freqs[i]
# sys_freq = list(set(union_list))
sys_freq = sat_freqs[0]
"""Initialize the dictionaries"""
dd_means = {}
dd_stds = {}
for file in files:
    dd_means[file] = []
    dd_stds[file] = []

ii = 0
for dut in sat_freqs:
    jj = 0
    for freq in dut:
        if freq in sys_freq:
            dd_means[files[ii]].append(mean_values[ii][jj])
            dd_stds[files[ii]].append(std_values[ii][jj])
        else:
            dd_means[files[ii]].append(0)
            dd_stds[files[ii]].append(0)
        jj += 1
    ii += 1
x = np.arange(len(sys_freq))
width = 0.25
multiplier = 0
colors = ["red", "green", "blue", "black", "orange", "yellow"]
fig, ((ax0, ax1)) = plt.subplots(nrows=2, ncols=1)
# ii = 0
for keys, values in dd_means.items():
    offset = width*multiplier
    rects0 = ax0.bar(x+offset, values, width, label=keys, color=colors[multiplier])
    ax0.bar_label(rects0, padding=0)
    multiplier += 1
ax0.set_ylabel('m')
ax0.set_title('mean value of double difference')
ax0.set_xticks(x+(len(files)-1)/2*width, sys_freq)
ax0.legend(loc='upper left', ncols=5)
ax0.set_ylim(0, max(max(mean_values))+3)

multiplier = 0
for keys, values in dd_stds.items():
    offset = width*multiplier
    rects1 = ax1.bar(x+offset, values, width, label=keys, color="white", edgecolor=colors[multiplier], linewidth=4)
    ax1.bar_label(rects1, padding=3)
    multiplier += 1
ax1.set_ylabel('m')
ax1.set_title('standard deviation of double difference')
ax1.set_xticks(x + (len(files)-1)/2*width, sys_freq)
ax1.legend(loc='upper left', ncols=5)
ax1.set_ylim(0, max(max(std_values))+5)

plt.show(block=True)
