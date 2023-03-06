# Data : 2023/3/3 16:19
# Author: Shawn Shi
# Right Reserved By COROS
"""
MTK raw PVT parser

Usage:
    python mtk-raw-pvt-parser.py [--no-flow-control] <file>
"""
import math
import matplotlib.pyplot as plt
import os
import struct
import sys
from tkinter import filedialog

import tkinter as tk


def calc_checksum(checksum_range: bytes) -> int:
    checksum_calc = checksum_range[0]
    for it in checksum_range[1:]:
        checksum_calc ^= it
    return checksum_calc


def convert_flow_control(data: bytes) -> bytes:
    converted_bytes = bytearray()
    need_convert = False
    for it in data:
        if need_convert:
            converted_bytes.append(0xff - it)
            need_convert = False
            continue
        if it == 0x77:
            need_convert = True
            continue
        converted_bytes.append(it)
    return converted_bytes


def parse(data: bytes, flow_control=True, check_checksum=True):
    preamble = b'\x04\x24'
    end = b'\xAA\x44'
    start_pos = 0
    checksum_error_cnt = 0
    while True:
        start_pos = data.find(preamble, start_pos)
        if start_pos == -1:
            break
        end_pos = data.find(end, start_pos)
        if end_pos == -1:
            break

        message_bytes = data[start_pos:end_pos + 2]
        start_pos = end_pos + 2

        if not message_bytes:
            continue

        if flow_control:
            message_bytes = convert_flow_control(message_bytes)

        if check_checksum:
            checksum_calc = calc_checksum(message_bytes[2:-3])  # message_bytes[2:-3]
            if checksum_calc != message_bytes[-3]:
                checksum_error_cnt += 1
                continue

        message_id = struct.unpack('<H', message_bytes[2:4])[0]
        if message_id != 4005:
            continue
        length = int.from_bytes(message_bytes[4:6], byteorder='little')
        msg_data = message_bytes[6:6 + length]
        if len(msg_data) != 120:
            continue

        datadict = {}
        (
            datadict['iod'],  # U1
            datadict['fix_type'],  # U1
            datadict['year'],  # U2
            datadict['month'],  # U1
            datadict['day'],  # U1
            datadict['hour'],  # U1
            datadict['minute'],  # U1
            datadict['ms'],  # U2
            datadict['second'],  # U1
            pvt_status,  # U1,
            datadict['lat'],  # I4
            datadict['lon'],  # I4
            datadict['alt'],  # I4
            datadict['geoid'],  # I4
            datadict['speed'],  # U4
            datadict['heading'],  # U4
            datadict['horizontal_accuracy'],  # R4
            datadict['lsq_lat'],  # I4
            datadict['lsq_lon'],  # I4
            datadict['lsq_alt'],  # I4
            datadict['lsq_velocity_N'],  # I4
            datadict['lsq_velocity_E'],  # I4
            datadict['lsq_velocity_D'],  # I4
            datadict['lsq_clock_bias'],  # R8
            datadict['lsq_clock_drift'],  # R8
            datadict['kf_lat'],  # I4
            datadict['kf_lon'],  # I4
            datadict['kf_alt'],  # I4
            datadict['kf_velocity_N'],  # I4
            datadict['kf_velocity_E'],  # I4
            datadict['kf_velocity_D'],  # I4
            datadict['kf_clock_bias'],  # R8
            datadict['kf_clock_drift'],  # R8
        ) = struct.unpack('<BBHBBBBHBBiiiiIIfiiiiiiddiiiiiidd', msg_data)
        datadict['lla_valid'] = bool(pvt_status & 0b1)
        datadict['lsq_valid'] = bool(pvt_status >> 1 & 0b1)
        datadict['kf_valid'] = bool(pvt_status >> 2 & 0b1)

        yield datadict

    print("Checksum error", checksum_error_cnt, file=sys.stderr)


def create_kml(time_name, cor_str):
    if len(cor_str):
        read_data(cor_str, "gps_ori_data.kml", "%s.kml" % time_name)


def read_data(gps_data, file_kml, path):
    """传入经纬度信息写入kml文件，区分原始数据与算法处理过的数据"""
    with open(file_kml, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    for i in range(len(lines) - 1):
        if '<coordinates>' in lines[i]:
            lines[i] = '<coordinates>' + gps_data + '</coordinates>\n'
    with open(path, 'w', encoding='utf-8') as fi:
        fi.writelines(lines)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    print('---------LSQ data output tool version 1.0.0-----------')
    print('-----------All rights are reserved by COROS------------')
    file = filedialog.askopenfile()
    if not file:
        sys.exit("******未选择任何文件，自动退出程序！！！******")
    path = os.path.dirname(file.name)
    lsq_coord = []
    kf_coord = []
    # calculate velocity, vertical velocity excluded
    lsq_velocity = []
    kf_velocity = []
    # Clock bias and drift
    lsq_clock_bias = []
    lsq_clock_drift = []
    kf_clock_bias = []
    kf_clock_drift = []
    # n = 0
    # m = 0
    flow_control = False
    check_checksum = True
    with open(file.name, 'rb') as f:
        data = f.read()
        # n = n+1
        for it in parse(data, flow_control, check_checksum):
            if it['lsq_valid']:
                # m = m+1
                lsq_coord.extend([str(it['lsq_lon'] / 1e7), str(it['lsq_lat'] / 1e7), '0'])
                lsq_velocity.append(math.sqrt(it['lsq_velocity_E'] ** 2 + it['lsq_velocity_N'] ** 2) / 1000)
                lsq_clock_bias.append(it['lsq_clock_bias'])
                lsq_clock_drift.append(it['lsq_clock_drift'])
            if it['kf_valid']:
                kf_coord.extend([str(it['kf_lon'] / 1e7), str(it['kf_lat'] / 1e7), '0'])
                kf_velocity.append(math.sqrt(it['kf_velocity_E'] ** 2 + it['kf_velocity_N'] ** 2)/100)
                kf_clock_bias.append(it['kf_clock_bias'])
                kf_clock_drift.append(it['kf_clock_drift'])
            print(it)
        # print(m)
        # print(n)
        lsq_coord_data = ','.join(lsq_coord).replace(',0,', ',0 ')
        kf_coord_data = ','.join(kf_coord).replace(',0,', ',0 ')
    create_kml(file.name[:-4] + '_lsq_coordinates', lsq_coord_data)
    create_kml(file.name[:-4] + '_kf_coordinates', kf_coord_data)
    # plot velocity information
    plt.figure()
    plt.plot(list(range(len(lsq_velocity))), lsq_velocity, 'r', linewidth=2, label='LSQ Horizontal velocity')
    plt.plot(list(range(len(kf_velocity))), kf_velocity, 'b', linewidth=2, label='KF Horizontal velocity')
    plt.legend()
    plt.xlabel('epoch/s')
    plt.ylabel('m/s')
    plt.title(' LSQ velocity vs Kf velocity')
    # plot clock bias
    plt.figure()
    plt.plot(list(range(len(lsq_clock_bias))), lsq_clock_bias, 'r', linewidth=2, label='LSQ clock bias')
    plt.plot(list(range(len(kf_clock_bias))), kf_clock_bias, 'b', linewidth=2, label='KF clock bias')
    plt.legend()
    plt.xlabel('epoch/s')
    plt.ylabel('m')
    plt.title(' LSQ clock bias vs Kf clock bias')
    # plot clock drift
    plt.figure()
    plt.plot(list(range(len(lsq_clock_drift))), lsq_clock_drift, 'r', linewidth=2, label='LSQ clock drift')
    plt.plot(list(range(len(kf_clock_drift))), kf_clock_drift, 'b', linewidth=2, label='KF clock drift')
    plt.legend()
    plt.xlabel('epoch/s')
    plt.ylabel('m/s')
    plt.title(' LSQ clock bias vs Kf clock drift')
    plt.show(block=True)
