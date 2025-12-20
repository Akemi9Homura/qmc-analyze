"""
其他形式的可观测量估计方法，
"""

import numpy as np


# growth estimator，效果类似 norm-projected estimator
def cal_growth_estimator(trace, dtau, drop_ratio, state=0):
    if not (0.0 <= drop_ratio < 1.0):
        raise ValueError("drop_ratio 必须在 [0, 1) 范围内，例如 0.2 表示丢弃前 20%")

    steps = np.asarray(trace["steps"], dtype=int)
    Nw_arr = np.asarray(trace["Nw"][state], dtype=float)
    S_arr = np.asarray(trace["S"][state], dtype=float)
    n = steps.size
    interval = steps[1] - steps[0]
    drop_n = int(n * drop_ratio)
    if drop_n >= n:
        raise ValueError("丢弃的点数不少于总长度，无法计算平均值。")

    S_arr = S_arr[drop_n:]
    Nw_arr = Nw_arr[drop_n:]
    n = len(S_arr)
    Egr = np.zeros(n - 1, dtype=float)
    for i in range(1, n):
        Egr[i - 1] = (
            S_arr[i - 1]
            - (Nw_arr[i] - Nw_arr[i - 1]) / (interval * dtau * Nw_arr[i - 1])
            if Nw_arr[i - 1] != 0
            else 0.0
        )
    Egr_mean = np.mean(Egr)
    return Egr_mean
