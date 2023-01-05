# Data : 2023/1/5 10:29
# Author: Shawn Shi
# Right Reserved By COROS
# Data : 12/22/2022 5:46 PM
# Author: Shawn Shi
# Right Reserved By COROS
import numpy as np


def shift_evaluate2(std, track):
    ssd = track.shape
    # interpolation measured trajectory points
    track_inter = np.array([track[0]])
    if ssd[0] > 1 and ssd[1] == 2:
        max_inter = 2
        pad_idx = 0
        for i in range(1, ssd[0] - 1):
            pad_num = 1
            pad_idx = pad_idx + 1
            track_inter = np.append(track_inter, [track[i]], axis=0)  # track_inter[pad_idx, :] = track[i, :]
            inter = np.sqrt(sum((track[i] - track[i + 1]) ** 2))
            while inter > pad_num * max_inter:
                pad_num = pad_num + 1
                pad_idx = pad_idx + 1
                track_inter = np.append(
                    track_inter, [track_inter[pad_idx - 1] + (track[i + 1] - track[i]) * max_inter / inter],
                    axis=0)
                # track_inter[pad_idx, :] = track_inter[pad_idx - 1, :] + (track[i + 1, :] - track[i, :]) * max_inter /
                # inter
        track_inter = np.append(track_inter, [track[-1]], axis=0)
    # strack = track_inter.shape
    Cs = np.average(std, axis=0)
    Ct = np.average(track_inter, axis=0)
    shift = Ct - Cs

    return shift
