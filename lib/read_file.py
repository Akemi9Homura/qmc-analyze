import numpy as np
import sys


# 读取非 replica 的 trace 文件
def read_normal_trace_file(filename):
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


# 读取 replica 的 trace，这个可能更对，log 输出的 E 与 J2 已经把 norm 除掉了
# 应该分子分母分别平均，再相除
def read_replica_trace_file(filename):
    data = np.loadtxt(filename, comments="#", delimiter=",", unpack=True)
    step, sidx, replica_E, replica_J2, norm = data

    steps = np.unique(step)
    steps.sort()
    unique_sidx = np.unique(sidx)
    unique_sidx.sort()

    # 将数据按态分类存储
    arrays_list = [replica_E, replica_J2, norm]
    result_arrays = [[arr[sidx == idx] for idx in unique_sidx] for arr in arrays_list]
    replica_E_arrays, replica_J2_arrays, norm_arrays = result_arrays

    # 每一个态的数据是一个 numpy 数组
    trace = {
        "steps": steps,
        "E": replica_E_arrays,
        "J2": replica_J2_arrays,
        "norm": norm_arrays,
    }

    return trace


def read_trace_auto(filename):
    """
    自动判断 trace 文件类型（replica / non-replica，也就是 normal），
    调用对应的 read 函数。

    返回
    ----
    trace : dict
        trace 数据
    trace_type : str
        "replica" 或 "normal"
    """
    # --- 读取 header ---
    header = None
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                header = line.lstrip("#").strip()
                break
            else:
                # 没有 header，直接退出
                break

    if header is None:
        raise ValueError("未能读取到 trace 文件的 header，无法判断类型")

    header_lower = header.lower()

    # --- 判断类型 ---
    if "replica_e" in header_lower:
        trace = read_replica_trace_file(filename)
        trace_type = "replica"
    elif "nw" in header_lower and "s" in header_lower:
        trace = read_normal_trace_file(filename)
        trace_type = "normal"
    else:
        raise ValueError(f"无法识别 trace 类型，header 为:\n{header}")

    return trace, trace_type


# 暂时的读取 replica log 文件的函数
# 需要读取的行形如 "sidx = 0: Replica E = -9.99271277, J2 = 0.66412419"
# 当前只支持 NS = 1，只读一个态
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

    print(f"共取到 {len(arr)} 个数据点。")

    log = {
        "E": arr["E"].copy(),  # 拷贝成普通的 1D array
        "J2": arr["J2"].copy(),
    }
    return log


def read_replica_log_interval(filename, interval=10):
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

    # 原先的写法是第 10 步开始输出，每隔 10 步输出一次
    # 原输出的第 10 步对应的是程序的第 100 步，每隔 10 步读取也对应程序的每隔 100 步输出
    arr = arr[9::interval]

    print(f"共取到 {len(arr)} 个数据点。")

    log = {
        "E": arr["E"].copy(),  # 拷贝成普通的 1D array
        "J2": arr["J2"].copy(),
    }
    return log
