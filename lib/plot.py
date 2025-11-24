import numpy as np
import matplotlib.pyplot as plt
from .block import *

def simple_plot_trace(trace, state=0, step_end=None):
    """
    绘制 trace 中某个态的 S 和 E/norm 随 steps 的变化曲线。
    
    参数
    ----
    trace : dict
        read_trace_file() 返回的字典
    state : int
        要绘图的态编号（默认 0，即第一个态）
    end : int
        画到的步数：
        - 必须是正整数，否则报错
        - 如果 end > 最大的 step，则画全程
        - 如果 steps 中没有 end，则画到最接近 end 的那个 step
    """
    steps = trace["steps"]  # 一维数组
    
    # --- 默认值：如果不传，就是整个区间 ---
    if step_end is None:
        step_end = int(steps[-1])

    # --- step_end 对应的索引 ---
    end_index = np.searchsorted(steps, step_end, side="right")
    if end_index == 0 or steps[end_index - 1] != step_end:
        raise ValueError(f"未找到 step_end = {step_end}")

    # 取指定态的数据
    S = trace["S"][state]
    E = trace["E"][state]
    norm = trace["norm"][state]

    # 做同样的切片，保证长度一致
    steps_plot = steps[:end_index]
    S_plot = S[:end_index]
    E_plot = E[:end_index]
    norm_plot = norm[:end_index]

    Enorm_plot = E_plot / norm_plot

    # --- 画图 ---
    plt.figure(figsize=(8, 5))

    plt.plot(steps_plot, S_plot, label="S", color='green',linewidth=0.5)
    plt.plot(steps_plot, Enorm_plot, label="E / norm",color='red', linewidth=1)

    plt.xlabel("Steps")
    plt.ylabel("E (MeV)")
    plt.title(f"Trace Plot (state {state}, end={step_end})")
    plt.legend()
    plt.tight_layout()
    plt.show()

def simple_plot_block(trace, state=0, step_start=None, step_end=None):
    """
    对给定态在指定 step 区间做块分析，并画出 std_err 随 block_size 的变化。
    默认分析整个 steps 区间。
    """
    steps = trace["steps"]

    # --- 默认值：如果不传，就是整个区间 ---
    if step_start is None:
        step_start = int(steps[0])
    if step_end is None:
        step_end = int(steps[-1])

    # --- step_start 对应的索引 ---
    start_index = np.searchsorted(steps, step_start, side="left")
    if start_index >= len(steps) or steps[start_index] != step_start:
        raise ValueError(f"未找到 step_start = {step_start}")

    # --- step_end 对应的索引 ---
    end_index = np.searchsorted(steps, step_end, side="right")
    if end_index == 0 or steps[end_index - 1] != step_end:
        raise ValueError(f"未找到 step_end = {step_end}")

    # --- 截取对应区间 ---
    E_seg = trace["E"][state][start_index:end_index]
    norm_seg = trace["norm"][state][start_index:end_index]
    S_seg = trace["S"][state][start_index:end_index]

    # --- 块分析 ---
    std_errs, std_err_errs = block_analysis_energy(E_seg, norm_seg)
    std_errs_S, std_err_errs_S = block_analysis(S_seg)
    
    n=len(std_errs)
    if len(std_errs_S) != n:
        raise RuntimeError("E 和 S 的块分析结果长度不一致，请检查 block_analysis 实现。")

    # block_size = 1,2,4,...,2^(n-1)
    lengths = [1 << i for i in range(n)]

    # --- 画图 ---
    plt.figure(figsize=(7, 5))
    # E 的误差条
    plt.errorbar(
        lengths,
        std_errs,
        yerr=std_err_errs,
        color='red',
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
        color='blue',
        fmt="s--",
        capsize=4,
        linewidth=1.5,
        markersize=5,
        label="S",
    )

    plt.xscale("log")
    plt.xlabel("Block size L")
    plt.ylabel("sigma")
    plt.title(f"Block analysis (state={state}, step {step_start} → {step_end})")

    plt.tight_layout()
    plt.show()
    # plt.savefig('block_analysis.png', dpi=600)
