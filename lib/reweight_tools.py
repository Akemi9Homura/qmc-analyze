"""
  Module for reweighting calculations in FCIQMC analysis.
"""

import numpy as np
from .cal import *

# 计算 dtau，按照代码的写法写，输入是 FCIQMC 的输入
def compute_dtau(dtau):
    hbar = 0.6582119460238695 # MeV zs
    return dtau / hbar

# 计算权重 W_{Cn}，对每个满足给定 n order 能计算的 step 都计算，返回 array
def cal_reweight_factor(trace, dtau, order, drop_ratio,state=0):
    """
    丢弃前 drop_ratio 比例的数据
    drop_ratio: 0~1 之间的小数，例如 0.2 表示丢弃前 20%
    """
    if not (0.0 <= drop_ratio < 1.0):
        raise ValueError("drop_ratio 必须在 [0, 1) 范围内，例如 0.2 表示丢弃前 20%")

    steps = np.asarray(trace["steps"], dtype=int)
    S_arr = np.asarray(trace["S"][state], dtype=float)
    n = steps.size
    
    interval = steps[1] - steps[0]

    drop_n = int(n * drop_ratio)
    if drop_n >= n:
        raise ValueError("丢弃的点数不少于总长度，无法计算平均值。")

    # 确定了计算的起始位置与其 idx，steps 是没丢弃前百分比的，因此 S_arr 也不能丢弃
    cut_step = steps[drop_n]
    start_step = cut_step + order
    if start_step % interval != 0:
        # start_step 向上取整到最近的可用 step
        start_step = ((start_step + interval - 1) // interval) * interval
    if start_step > steps[-1]:
        raise ValueError(f"丢弃数据后，剩余数据无法满足给定 order = {order} 的计算。")
    start_idx = np.searchsorted(steps, start_step)
    length = len(steps) - start_idx
    if length <= 0:
        raise ValueError(f"丢弃数据后，剩余数据无法满足给定 order = {order} 的计算。")
    
    logW = np.zeros(length, dtype=float)
    es = cal_mean(trace["S"][state], drop_ratio)
    ee = cal_mean(trace["E"][state], drop_ratio)
    enorm = cal_mean(trace["norm"][state], drop_ratio)
    ee /= enorm
    C = es
    print(f"Reweighting parameters: <S> = {es}, <E> = {ee}")
    for i in range(length):
        idx = start_idx + i
        step_x1 = steps[idx] - order
        step_x2 = steps[idx] - 1
        sum_S = sum_S_x1x2(S_arr, steps, step_x1, step_x2, interval)
        logW[i] = -dtau * (sum_S- order * C)
    
    W = np.exp(logW)
    return start_idx, W
        

# 给定 step x1 与 x2，一共的数据数就是 n = order 个，用这些 S 加起来
def sum_S_x1x2(S_data, steps, x1, x2, A):
    """
    计算从 step x1 到 x2 的 S 之和。
    S_data: S值的数组 (numpy array)
    steps:  对应的步数数组 (numpy array)
    x1, x2: 起始步和结束步 (闭区间 [x1, x2])
    A:      间隔 (interval)
    """
    
    total_sum = 0.0
    
    # 1. 计算对齐边界
    # ceil_x1: 左侧碎片结束点 (向上取整到 A 的倍数)
    # floor_x2: 中间完整块结束点 (向下取整到 A 的倍数)
    ceil_x1 = ((x1 - 1) // A + 1) * A
    floor_x2 = (x2 // A) * A

    # --- 情况 A: x1 和 x2 在同一个 S 块内 (例如 34-38) ---
    if ceil_x1 > floor_x2:
        # 直接查找 ceil_x1 对应的 S
        idx = np.searchsorted(steps, ceil_x1)
        if idx < len(steps) and steps[idx] == ceil_x1:
            count = x2 - x1 + 1
            total_sum += count * S_data[idx]
        return total_sum

    # --- 情况 B: 跨越多个块 (例如 34-53) ---
    # 1. 左碎片 (Left Fragment): [x1, ceil_x1]
    left_count = ceil_x1 - x1 + 1
    if left_count > 0:
        idx = np.searchsorted(steps, ceil_x1)
        if idx < len(steps) and steps[idx] == ceil_x1:
            total_sum += left_count * S_data[idx]

    # 2. 中间完整块 (Middle Blocks): (ceil_x1, floor_x2]
    # 只有当 floor_x2 确实大于 ceil_x1 时才存在中间整块
    if floor_x2 > ceil_x1:
        # 查找切片范围
        # idx_start: ceil_x1 之后的位置 (跳过 ceil_x1)
        # idx_end: floor_x2 之后的位置 (切片包含 floor_x2)
        idx_start = np.searchsorted(steps, ceil_x1, side='right')
        idx_end = np.searchsorted(steps, floor_x2, side='right')
        
        # 利用切片直接求和并乘 A
        mid_sum = np.sum(S_data[idx_start : idx_end])
        total_sum += mid_sum * A

    # 3. 右碎片 (Right Fragment): (floor_x2, x2]
    right_count = x2 - floor_x2
    if right_count > 0:
        target_step = floor_x2 + A
        idx = np.searchsorted(steps, target_step)
        if idx < len(steps) and steps[idx] == target_step:
            total_sum += right_count * S_data[idx]

    return total_sum

# 计算加权能量
def cal_reweight_energy(E_data, norm_data,start_idx, W):
    """
    计算加权能量 <E>_W = sum (E_i*W_i) / sum(norm_i * W_i)
    E_data: 能量数组 (numpy array)
    norm_data: 归一化数组 (numpy array)
    W: 权重数组 (numpy array)
    """
    E_data = E_data[start_idx:]
    norm_data = norm_data[start_idx:]
    if len(E_data) != len(W) or len(norm_data) != len(W):
        raise ValueError("E_data, norm_data 与 W 的长度必须相同。")
    weighted_E = np.sum(W * E_data)
    sum_W = np.sum(W * norm_data)
    if sum_W == 0:
        raise ValueError("权重和为零，无法计算加权能量。")
    return weighted_E / sum_W

# 计算重加权的 S
def cal_reweight_S(trace, dtau, order, drop_ratio,state=0):
    start_idx_n, W_n = cal_reweight_factor(trace, dtau, order, drop_ratio=drop_ratio, state=state)
    start_idx_n1, W_n1 = cal_reweight_factor(trace, dtau, order+10, drop_ratio=drop_ratio, state=state)
    
    # 检查
    if len(W_n) != len(W_n1):
        if len(W_n) != len(W_n1) + 1:
            raise ValueError("计算重加权 S 时，W_n 长度应该为 W_n1 加 1。")
    
    steps = np.asarray(trace["steps"], dtype=int)
    interval = steps[1] - steps[0]
    Nw_arr = np.asarray(trace["Nw"][state], dtype=float)
    S_arr = np.asarray(trace["S"][state], dtype=float)
    C = cal_mean(S_arr, drop_ratio)
    
    start_step_n = steps[start_idx_n]
    start_step_n1 = steps[start_idx_n1]
    if start_step_n1 != start_step_n + interval:
        raise ValueError("计算重加权 S 时，start_idx_n1 对应的 step 应该比 start_idx_n 多一个间隔。")

    Wn_seg = W_n[:-1]
    Wn1_seg = W_n1
    Nn_seg = Nw_arr[start_idx_n:-1]
    Nn1_seg = Nw_arr[start_idx_n1:]
    # 检查
    if len(Wn_seg) != len(Wn1_seg) or len(Wn_seg) != len(Nn_seg) or len(Wn_seg) != len(Nn1_seg):
        raise ValueError("计算重加权 S 时，各数组长度不匹配。")
    
    # 计算 S
    reweight_S = C- (1/(interval*dtau)) * np.log( np.sum(Wn1_seg * Nn1_seg) / np.sum(Wn_seg * Nn_seg) )
    
    return reweight_S