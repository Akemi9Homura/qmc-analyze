"""
计算模块，在 numpy 内置的函数基础上做一些本程序需要使用的计算
"""

import numpy as np


# 计算单数据的均值，丢弃开头一定百分比的数据。可用于计算 S 与 J2 均值，输入的是对应 state 的列
def cal_mean(data, drop_ratio):
    """
    丢弃前 drop_ratio 比例的数据，返回剩余部分的平均值。
    data: 一维数组或可迭代对象
    drop_ratio: 0~1 之间的小数，例如 0.2 表示丢弃前 20%
    """
    if not (0.0 <= drop_ratio < 1.0):
        raise ValueError("drop_ratio 必须在 [0, 1) 范围内，例如 0.2 表示丢弃前 20%")

    arr = np.asarray(data, dtype=float)
    n = arr.size
    if n == 0:
        raise ValueError("data 为空，无法计算平均值。")

    drop_n = int(n * drop_ratio)
    if drop_n >= n:
        raise ValueError("丢弃的点数不少于总长度，无法计算平均值。")

    tail = arr[drop_n:]
    return tail.mean()
