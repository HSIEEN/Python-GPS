import numpy as np
import matplotlib.pyplot as plt
from track_parser import track_parser
from shift_evaluate import shift_evaluate
from HausdorffDist import HausdorffDist
import glob
import xlwings as xw

filelist1 = [file for file in glob.glob('./*.kml')]
filelist2 = [file for file in glob.glob('./*.gpx')]
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
    wb.save('TrajectoryDeviation.xls')
    wb.sheets['Sheet1'].name = 'data'
    ws = wb.sheets['data']
    ws.range('A1').value = '轨迹名称'
    ws.range('B1').value = '平均距离(m)'
    ws.range('C1').value = '最大距离(m)'
    ws.range('D1').value = '东向偏移(m)'
    ws.range('E1').value = '北向偏移(m)'
    ws.range('F1').value = '平移后平均距离(m)'
    ws.range('G1').value = '平移后最大距离(m)'
    ws.range('A1:G1').color = (255, 217, 100)
    ws.range('A1:G1').column_width = 20
    ws.range('A1:G100').api.HorizontalAlignment = -4108
    row = 1
    for file in filelist:
        n = len(filelist)
        if track_dims[file][0] > 0 and track_dims[file][1] == 2:
            row = row+1
            ws.range('A'+str(row)).value = file[2:-4]
            hd19, mhd19 = HausdorffDist(std_pad, track_data[file], 'visual')
            shift = shift_evaluate(std_pad, track_data[file])
            track_revised = track_data[file] + shift
            hd19R, mhd19R = HausdorffDist(std_pad, track_revised, 'visual')
            # write_data(filename, )
            ws.range('B' + str(row)).value = str(round(mhd19, 2))
            ws.range('C' + str(row)).value = str(round(hd19, 2))
            ws.range('D' + str(row)).value = str(round(-shift[0], 2))
            ws.range('E' + str(row)).value = str(round(-shift[1], 2))
            ws.range('F' + str(row)).value = str(round(mhd19R, 2))
            ws.range('G' + str(row)).value = str(round(hd19R, 2))
            print('*******************************************************')
            print('%s:\n' % file[2:-4])
            print('    MAX_ERROR = %.2f(m)\n    MEAN_ERROR = %.2f(m)\n' % (hd19, mhd19))
            print('    shift_lon = %.2f(m)\n    shift_lat = %.2f(m)\n' % (-shift[0], -shift[1]))
            print('    MAX_ERROR after shift = %.2f(m)\n    MEAN_ERROR after shift = %.2f(m)' % (hd19R, mhd19R))
            # plt.subplot(1, n, i)
            plt.figure()
            plt.plot(std_pad[:, 0], std_pad[:, 1], 'r', linewidth=2, label='RTK_Track')
            plt.plot(track_data[file][:, 0], track_data[file][:, 1], 'g', linewidth=2, label='Initial: ' +
                                                                                             'Shift: East=' + str(
                round(-shift[0], 2)) + 'm, ' + 'North=' + str(round(-shift[1], 2)) + 'm\n' +
                                                                                             'Max_' + str(
                round(hd19, 2)) + 'm_Mea_' + str(round(mhd19, 2)) + 'm')
            plt.plot(track_revised[:, 0], track_revised[:, 1], 'b', linewidth=2, label='Shifted: ' +
                                                                                       'Max_' + str(
                round(hd19R, 2)) + 'm_Mea_' + str(round(mhd19R, 2)) + 'm')
            plt.legend()
            plt.xlabel('East (m)')
            plt.ylabel('North (m)')
            plt.title(file[2:-4])
            plt.savefig(file[2:-4])
            # plt.subplot(1, 2, 2)
            # b = plt.bar([1, 2, 3], np.array([hd19, hd16, hd1619]))
            # plt.xlabel('1-B19:Std;  2-B16:Std;  3-B19:B16')
            # plt.ylabel('Hausdorff Distance (m)')
            # plt.title('Hausdorff Distance of Three tracks')

        else:
            print('Trajectory data does not exist!\n' % ())
    plt.show()
else:
    print('Standard Track is NULL!\n' % ())
print('Press Enter key to exit....')
input()
exit()
