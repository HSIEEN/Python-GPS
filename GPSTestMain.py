import numpy as np
import matplotlib.pyplot as plt
from track_parser import track_parser
from shift_evaluate import shift_evaluate
from HausdorffDist import HausdorffDist
from track_length import track_length
import glob
import xlwings as xw
import tkinter as tk
from tkinter import filedialog
from shift_evaluate2 import shift_evaluate2

root = tk.Tk()
root.withdraw()
print('***************请选择要分析的文件目录****************')

file_path = filedialog.askdirectory()
if file_path == '':
    print("No directory was chosen, exit")
    exit()
filelist1 = [file for file in glob.glob(file_path + '/*.kml')]
filelist2 = [file for file in glob.glob(file_path + '/*.gpx')]
filelist = filelist1 + filelist2
standard_kml = ''
for file in filelist:
    if 'RTK' in file:
        standard_kml = file
if standard_kml == '':
    print('No RTK trajectory file found!!')
    exit()
filelist = [file for file in filelist if file != standard_kml]

# standard_kml = 'ZF2_RTKError.kml'
# kml_16 = '4TH_B20_1#_889592_G3B(L1)_R_2022-12-16 21_03_30.kml'
# kml_19 = '4TH_B20_S3#_6d8740_G3B(L1)_R_2022-12-16 21_03_28.kml'
# ##


std_track, start_lon, start_lat = track_parser(standard_kml)

track_data = {}
track_dims = {}
# get trajectory data
for file in filelist:
    track_data[file], __, __ = track_parser(file, start_lon, start_lat)
    track_dims[file] = track_data[file].shape
ssd = std_track.shape

std_pad = np.array([std_track[0]])
# std_pad = np.zeros((1, 2))
# interpolation among sparse points
if ssd[0] > 1 and ssd[1] == 2:
    max_inter = 3
    pad_idx = 0
    for i in range(1, ssd[0] - 1):
        pad_num = 1
        pad_idx = pad_idx + 1
        std_pad = np.append(std_pad, [std_track[i]], axis=0)  # std_pad[pad_idx, :] = std_track[i, :]
        inter = np.sqrt(sum((std_track[i] - std_track[i + 1]) ** 2))
        while inter > pad_num * max_inter:
            pad_num = pad_num + 1
            pad_idx = pad_idx + 1
            std_pad = np.append(
                std_pad, [std_pad[pad_idx - 1] + (std_track[i + 1] - std_track[i]) * max_inter / inter],
                axis=0)
            # std_pad[pad_idx, :] = std_pad[pad_idx - 1, :] + (std_track[i + 1, :] - std_track[i, :]) * max_inter /
            # inter
    std_pad = np.append(std_pad, [std_track[-1]], axis=0)
    wb = xw.Book()
    wb.save(file_path + '\\' + 'TrajectoryDeviation.xls')
    wb.sheets['Sheet1'].name = 'data'
    ws = wb.sheets['data']
    ws.range('A1').value = '轨迹名称'
    ws.range('B1').value = '平均距离(m)'
    ws.range('C1').value = '最大距离(m)'
    ws.range('D1').value = '东向偏移(m)'
    ws.range('E1').value = '北向偏移(m)'
    ws.range('F1').value = '总偏移量(m)'
    ws.range('G1').value = '平移后平均距离(m)'
    ws.range('H1').value = '平移后最大距离(m)'
    ws.range('I1').value = '图形标号'
    ws.range('A1:I1').color = (255, 217, 100)
    ws.range('A1:I1').column_width = 20
    ws.range('A1:I100').api.HorizontalAlignment = -4108
    ws.range('A2:A100').api.HorizontalAlignment = -4131
    row = 1
    for file in filelist:
        n = len(filelist)
        if track_dims[file][0] > 0 and track_dims[file][1] == 2:
            file_str = file.split("\\")
            filename = file_str[-1]
            filename = filename[:-4]
            row = row + 1
            ws.range('A' + str(row)).value = filename
            hd19, mhd19, shift1 = HausdorffDist(std_pad, track_data[file])
            shift2 = shift_evaluate(std_pad, track_data[file])
            shift = shift_evaluate2(std_pad, track_data[file])
            track_revised = track_data[file] - shift
            hd19R, mhd19R, _ = HausdorffDist(std_pad, track_revised)
            # write_data(filename, )
            ws.range('B' + str(row)).value = str(round(mhd19, 2))
            ws.range('C' + str(row)).value = str(round(hd19, 2))
            ws.range('D' + str(row)).value = str(round(shift[0], 2))
            ws.range('E' + str(row)).value = str(round(shift[1], 2))
            ws.range('F' + str(row)).value = str(round(np.sqrt(shift[0] ** 2 + shift[1] ** 2), 2))
            ws.range('G' + str(row)).value = str(round(mhd19R, 2))
            ws.range('H' + str(row)).value = str(round(hd19R, 2))
            ws.range('I' + str(row)).value = str('Figure ' + str(row - 1))
            print('*******************************************************')
            print('%s:\n' % filename)
            print('    MAX_ERROR = %.2f(m)\n    MEAN_ERROR = %.2f(m)\n' % (hd19, mhd19))
            print('    shift_lon = %.2f(m)\n    shift_lat = %.2f(m)\n' % (shift[0], shift[1]))
            print('    MAX_ERROR after shift = %.2f(m)\n    MEAN_ERROR after shift = %.2f(m)' % (hd19R, mhd19R))
            # plt.subplot(1, n, i)
            plt.figure()
            plt.plot(std_pad[:, 0], std_pad[:, 1], 'r', linewidth=2, label='RTK_Track')
            plt.plot(track_data[file][:, 0], track_data[file][:, 1], 'g', linewidth=2, label='Initial: ' +
                                                                                             'Max=' + str(
                round(hd19, 2)) + 'm, Mea=' + str(round(mhd19, 2)) + 'm\n'
                                                                     'Shift: East=' + str(
                round(-shift[0], 2)) + 'm, ' + 'North=' + str(round(-shift[1], 2)) + 'm')
            plt.plot(track_revised[:, 0], track_revised[:, 1], 'b', linewidth=2, label='Shifted: ' +
                                                                                       'Max=' + str(
                round(hd19R, 2)) + 'm, Mea=' + str(round(mhd19R, 2)) + 'm')
            plt.legend()
            plt.xlabel('East (m)')
            plt.ylabel('North (m)')
            plt.title(filename)
            plt.savefig(file_path + '\\' + filename + '.png')
            # plt.subplot(1, 2, 2)
            # b = plt.bar([1, 2, 3], np.array([hd19, hd16, hd1619]))
            # plt.xlabel('1-B19:Std;  2-B16:Std;  3-B19:B16')
            # plt.ylabel('Hausdorff Distance (m)')
            # plt.title('Hausdorff Distance of Three tracks')

        else:
            print('Trajectory data does not exist!\n' % ())
    wb.save()
    xw.App().quit()
    plt.show(block=True)
else:
    print('Standard Track is NULL!\n' % ())
