##
import numpy as np
import tkinter
import matplotlib.pyplot as plt
from track_parser import track_parser
from shift_count import shift_count
# import track_parser
from HausdorffDist import HausdorffDist
import glob

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

track_dict = {}
track_dims = {}
# get trajectory data
for file in filelist:
    track_dict[file], __, __ = track_parser(file, start_lon, start_lat)
    track_dims[file] = track_dict[file].shape
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
    for file in filelist:
        if track_dims[file][0] > 0 and track_dims[file][1] == 2:
            hd19, mhd19 = HausdorffDist(std_pad, track_dict[file], 'visual')
            shift = shift_count(std_pad, track_dict[file])
            track_revised = track_dict[file]+shift
            hd19R, mhd19R = HausdorffDist(std_pad, track_revised, 'visual')
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('%s:\n' % file[2:-4])
            print('    MAX_ERROR = %.2f(m)\n    MEAN_ERROR = %.2f(m)\n' % (hd19, mhd19))
            print('    shift_lon = %.2f(m)\n    shift_lat = %.2f(m)\n' % (shift[0], shift[1]))
            print('    MAX_ERROR after shift = %.2f(m)\n    MEAN_ERROR after shift = %.2f(m)' % (hd19R, mhd19R))
            # plt.subplot(1, 2, 1)
            # plt.plot(std_pad[:, 0], std_pad[:, 1], 'r', linewidth=2, label='Std')
            # plt.plot(B19_Track[:, 0], B19_Track[:, 1], 'g', linewidth=2, label='B19')
            # plt.plot(B16_Track[:, 0], B16_Track[:, 1], 'b', linewidth=2, label='B16')
            # plt.legend()
            # plt.xlabel('East (m)')
            # plt.ylabel('North (m)')
            # plt.title('Three tracks to compare')
            # plt.subplot(1, 2, 2)
            # b = plt.bar([1, 2, 3], np.array([hd19, hd16, hd1619]))
            # plt.xlabel('1-B19:Std;  2-B16:Std;  3-B19:B16')
            # plt.ylabel('Hausdorff Distance (m)')
            # plt.title('Hausdorff Distance of Three tracks')
            # plt.show()
        else:
            print('Trajectory data does not exist!\n' % ())
else:
    print('Standard Track is NULL!\n' % ())
print('Press Enter key to exit....')
input()
