import numpy as np
import sys


# 读取 trace 文件
def read_trace_file(filename, num_state=1):
    # 在胡师兄代码的启发下用 np 读取更快
    data = np.loadtxt(filename, comments="#", delimiter=",", unpack=True)
    step, sidx, Nw, S, E, J2, norm = data

    steps = np.unique(step)
    steps.sort()
    unique_sidx = np.unique(sidx)
    unique_sidx.sort()

    # 将数据按态分类存储
    arrays_list = [Nw, S, E, J2, norm]
    result_arrays = [[arr[sidx == idx] for idx in unique_sidx] for arr in arrays_list]
    Nw_arrays, S_arrays, E_arrays, J2_arrays, norm_arrays = result_arrays

    # 每一个态的数据是一个 numpy 数组
    trace = {
        "steps": steps,
        "Nw": Nw_arrays,
        "S": S_arrays,
        "E": E_arrays,
        "J2": J2_arrays,
        "norm": norm_arrays,
    }

    return trace
