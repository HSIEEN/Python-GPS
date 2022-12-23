import numpy as np
import math as mt
import re


def track_parser(track_path, lon0=0, lat0=0):
    global cur_lat, cur_lon
    track_points = []
    start_lon = 0
    start_lat = 0
    fpn = open(track_path, 'rt', encoding='utf-8')
    coord_line = 0
    coord_start = 0
    coord_end = 0

    if track_path[-4:] == '.kml':
        while True:
            src_str = fpn.readline()  # read a line of the text file
            if src_str != '':
                coord_start = [x.start() for x in re.finditer('<coordinates>', src_str)]  # src_str.find('<coordinates>')
                coord_end = [x.start() for x in re.finditer('</coordinates>', src_str)]  # strfind(src_str,'</coordinates>')
                if len(coord_start) != 0 and len(coord_end) != 0:
                    if coord_end[0] > len('<coordinates>') + 1:
                        coord_str = src_str[coord_start[0] + len('<coordinates>'):coord_end[0]]
                        track_points, start_lon, start_lat = spilt_points(coord_str, lon0, lat0)
                    break
                elif len(coord_start) != 0 and len(coord_end) == 0:
                    coord_line = 1
                elif len(coord_end) != 0:
                    break
                elif coord_line > 0:
                    track_points, start_lon, start_lat = spilt_points(src_str, lon0, lat0)
                    break
            else:
                break

    elif track_path[-4:] == '.gpx':  # str('.gpx') == str(track_path(np.arange(end() - 3, end() + 1))):
        coord_idx = 0
        start_lon = lon0
        start_lat = lat0
        while True:
            src_str = fpn.readline()  # read a line of the text file
            if src_str != '':
                coord_start = [x.start() for x in re.finditer(src_str, '<trkseg>')]  # strfind(src_str, '<trkseg>')
                coord_end = [x.start() for x in re.finditer(src_str, '</trkseg>')]  # strfind(src_str, '</trkseg>')
                trkpt = [x.start() for x in re.finditer(src_str, '<trkpt')]  # strfind(src_str, '<trkpt')
                if coord_end != 0:
                    break
                if coord_start != 0:
                    coord_line = 1
                if len(trkpt) != 0 and coord_line == 1:
                    # split string src_str with the specified character
                    pt_idx = [x.start() for x in re.finditer(src_str, '"')]  # strfind(src_str, '"')
                    lat_idx = [x.start() for x in re.finditer(src_str, 'lat=')]  # strfind(src_str, 'lat=')
                    lon_idx = [x.start() for x in re.finditer(src_str, 'lon=')]  # strfind(src_str, 'lon=')
                    if len(pt_idx) >= 4 and not len(lat_idx) == 0 and not len(lon_idx) == 0:
                        if lat_idx[1] > lon_idx[1]:
                            cur_lon = float(src_str[pt_idx[1] + 1:pt_idx[2] - 1])
                            cur_lat = float(src_str[pt_idx[3] + 1:pt_idx[4] - 1])
                        else:
                            cur_lon = float(src_str[pt_idx[1] + 1:pt_idx[2] - 1])
                            cur_lat = float(src_str[pt_idx[1] + 1:pt_idx[2] - 1])
                    coord_idx = coord_idx + 1
                    if coord_idx == 1 and start_lon < 1e-08 and start_lat < 1e-08:
                        start_lon = cur_lon
                        start_lat = cur_lat
                    x, y = calculate_coordinates(start_lon, start_lat, cur_lon, cur_lat)
                    track_points[coord_idx][1] = x
                    track_points[coord_idx][2] = y
                else:
                    break

    fpn.close()
    return track_points, start_lon, start_lat


def spilt_points(point_str=None, lon0=None, lat0=None):
    coord_idx = 0
    start_lon = lon0
    start_lat = lat0
    coord_list = point_str.split(' ')# strsplit(point_str,' ')
    coord_list = [i for i in coord_list if i != '']
    coord_num = len(coord_list)
    points_coord = np.zeros((coord_num, 2))
    for i in range(0, coord_num):
        if len(coord_list[i]) > 1:
            coord_idx = coord_idx + 1
            coord_item = coord_list[i].split(',')  # strsplit(coord_list[i],',')
            if coord_idx == 1 and start_lon < 1e-08 and start_lat < 1e-08:
                start_lon = float(coord_item[0])
                start_lat = float(coord_item[1])
            x, y = calculate_coordinates(start_lon, start_lat, float(coord_item[0]), float(coord_item[1]))
            points_coord[coord_idx-1, 0] = x
            points_coord[coord_idx-1, 1] = y

    points_coord = points_coord[0:coord_idx + 1, :]
    return points_coord, start_lon, start_lat


def calculate_coordinates(theta1=None, phi1=None, theta2=None, phi2=None):
    METERS_PER_RADIAN = 6378135.0
    RADIAN_2_DEGREE = 180 / np.pi
    MACHINE_PRECISION = 1e-08
    Dlon = theta2 - theta1
    Dlat = phi2 - phi1
    if np.abs(Dlon) <= MACHINE_PRECISION and np.abs(Dlat) <= MACHINE_PRECISION:
        arc = 0.0
        azimuth = 0.0
    else:
        sn1 = np.sin(phi1 / RADIAN_2_DEGREE)
        sn2 = np.sin(phi2 / RADIAN_2_DEGREE)
        cn1 = np.cos(phi1 / RADIAN_2_DEGREE)
        cn2 = np.cos(phi2 / RADIAN_2_DEGREE)
        arc0 = HaverSin(Dlat / RADIAN_2_DEGREE) + cn1 * cn2 * HaverSin(Dlon / RADIAN_2_DEGREE)
        arc1 = 2.0 * np.arcsin(np.sqrt(arc0))
        arc = arc1 * METERS_PER_RADIAN
        sn_arc = np.sin(arc1)
        if 1e-12 > sn_arc > - 1e-12:
            azimuth = 0.0
        else:
            sn = np.sin(Dlon / RADIAN_2_DEGREE) * cn2 / sn_arc
            cs = (sn2 * cn1 - cn2 * sn1 * np.cos(Dlon / RADIAN_2_DEGREE)) / sn_arc
            azimuth = mt.atan2(sn * 1000.0, cs * 1000.0)

    x = (arc * np.sin(azimuth))
    y = (arc * np.cos(azimuth))
    return x, y


def HaverSin(theta=None):
    v = np.sin(0.5 * theta)
    f = v * v
    return f


if __name__ == '__main__':
    track_parser("ZF2_RTKError.kml")
