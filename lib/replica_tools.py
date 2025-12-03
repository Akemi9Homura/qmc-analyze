import numpy as np
import matplotlib.pyplot as plt
from .block import *

"""
Replica 计算输出 log 暂时用的工具函数
"""


# 计算均值，丢弃开头一定百分比的数据
def replica_mean(data, drop_ratio):
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


# 块分析，丢弃开头一定百分比的数据
def plot_replica_block(data, drop_ratio):
    """
    丢弃前 drop_ratio 比例的数据
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
    std_errs, std_err_errs = block_analysis(tail)
    n = len(std_errs)
    lengths = [1 << i for i in range(n)]
    # --- 画图 ---
    plt.figure(figsize=(7, 5))
    plt.errorbar(
        lengths,
        std_errs,
        yerr=std_err_errs,
        color="red",
        fmt="o-",
        capsize=4,
        linewidth=1.5,
        markersize=5,
        label="E",
    )

    plt.xscale("log")
    plt.xlabel("Block size L")
    plt.ylabel("sigma")
    plt.title(f"Block analysis (after dropping {drop_ratio*100:.1f}%)")

    plt.tight_layout()
    plt.show()
