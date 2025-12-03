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


# 暂时的读取 replica log 文件的函数
# 需要读取的行形如 "sidx = 0: Replica E = -9.99271277, J2 = 0.66412419"
def read_replica_log(filename):
    """
    从输出文件中读取所有
    'Replica E = ..., J2 = ...'
    行，返回一个 dict，包含:
        log["E"]  -> numpy.ndarray
        log["J2"] -> numpy.ndarray
    """
    dt = np.dtype(
        [
            ("E", np.float64),
            ("J2", np.float64),
        ]
    )

    # Replica E = -9.99507344, J2 = 0.65899345
    pattern = r"Replica E\s*=\s*([+-eE0-9\.]+),\s*J2\s*=\s*([+-eE0-9\.]+)"

    arr = np.fromregex(filename, pattern, dt)

    log = {
        "E": arr["E"].copy(),  # 拷贝成普通的 1D array
        "J2": arr["J2"].copy(),
    }
    return log
