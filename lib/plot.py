import numpy as np
import matplotlib.pyplot as plt
from .block import *


def plot_trace(trace, state=0):
    """
    绘制 trace 中某个态的 S 和 E/norm 随 steps 的变化曲线。

    参数
    ----
    trace : dict
        read_trace_file() 返回的字典
    state : int
        要绘图的态编号（默认 0，即第一个态）
    """
    steps = trace["steps"]  # 一维数组

    # 取指定态的数据
    S = trace["S"][state]
    E = trace["E"][state]
    norm = trace["norm"][state]
    Enorm = E / norm

    # --- 画图 ---
    plt.figure(figsize=(8, 5))

    plt.plot(steps, S, label="S", color="green", linewidth=0.5)
    plt.plot(steps, Enorm, label="E", color="red", linewidth=1)

    plt.xlabel("Steps")
    plt.ylabel("E (MeV)")
    plt.title(f"Evol Plot (state {state})")
    plt.legend()
    plt.tight_layout()
    plt.show()


# 块分析能量，丢弃开头一定百分比的数据
def plot_block_e(trace, drop_ratio, state=0):
    """
    丢弃前 drop_ratio 比例的数据
    drop_ratio: 0~1 之间的小数，例如 0.2 表示丢弃前 20%
    """
    if not (0.0 <= drop_ratio < 1.0):
        raise ValueError("drop_ratio 必须在 [0, 1) 范围内，例如 0.2 表示丢弃前 20%")

    E_arr = np.asarray(trace["E"][state], dtype=float)
    norm_arr = np.asarray(trace["norm"][state], dtype=float)
    n = E_arr.size
    if n == 0:
        raise ValueError("data 为空，无法计算平均值。")

    drop_n = int(n * drop_ratio)
    if drop_n >= n:
        raise ValueError("丢弃的点数不少于总长度，无法计算平均值。")

    E_seg = E_arr[drop_n:]
    norm_seg = norm_arr[drop_n:]
    std_errs, std_err_errs = block_analysis_energy(E_seg, norm_seg)
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


# 块分析 S 与 E，画在一起
def plot_block_se(trace, drop_ratio, state=0):
    """
    丢弃前 drop_ratio 比例的数据
    drop_ratio: 0~1 之间的小数，例如 0.2 表示丢弃前 20%
    """
    if not (0.0 <= drop_ratio < 1.0):
        raise ValueError("drop_ratio 必须在 [0, 1) 范围内，例如 0.2 表示丢弃前 20%")

    E_arr = np.asarray(trace["E"][state], dtype=float)
    norm_arr = np.asarray(trace["norm"][state], dtype=float)
    S_arr = np.asarray(trace["S"][state], dtype=float)
    n = E_arr.size
    if n == 0:
        raise ValueError("data 为空，无法计算平均值。")

    drop_n = int(n * drop_ratio)
    if drop_n >= n:
        raise ValueError("丢弃的点数不少于总长度，无法计算平均值。")

    E_seg = E_arr[drop_n:]
    norm_seg = norm_arr[drop_n:]
    S_seg = S_arr[drop_n:]
    std_errs, std_err_errs = block_analysis_energy(E_seg, norm_seg)
    std_errs_S, std_err_errs_S = block_analysis(S_seg)

    if len(std_errs) != len(std_errs_S):
        raise ValueError("能量与 S 的块分析结果长度不一致！检查 block_analysis 函数。")

    n = len(std_errs)
    lengths = [1 << i for i in range(n)]
    # --- 画图 ---
    plt.figure(figsize=(7, 5))
    # E 的误差条
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
    # S 的误差条
    plt.errorbar(
        lengths,
        std_errs_S,
        yerr=std_err_errs_S,
        color="blue",
        fmt="s--",
        capsize=4,
        linewidth=1.5,
        markersize=5,
        label="S",
    )

    plt.xscale("log")
    plt.xlabel("Block size L")
    plt.ylabel("sigma")
    plt.title(f"Block analysis (after dropping {drop_ratio*100:.1f}%)")

    plt.tight_layout()
    plt.show()
