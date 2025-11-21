"""
主函数中定义的函数输入量全都是 trace，需要具体处理特定的数据结构
而不具体到 trace 结构的函数则放在 cal.py 中
"""

from lib.read_file import *
from lib.write_file import *
from lib.cal import *
from lib.block import *


# 计算 steps 的每一步开始的均值，结果存下来可用于画图
def analyze_trace_stable(trace, state=0):
    ES_arr = np.zeros(trace["steps"].size)
    EE_arr = np.zeros(trace["steps"].size)
    print(f"Analyzing trace for state {state}...")
    for i in range(trace["steps"].size):
        step = trace["steps"][i]
        # print(f"From step {step}:\n")
        mean_norm = cal_mean(i, trace["norm"][state])
        mean_S = cal_mean(i, trace["S"][state])
        mean_E = cal_mean(i, trace["E"][state]) / mean_norm
        ES_arr[i] = mean_S
        EE_arr[i] = mean_E
        # print(f"Mean S = {mean_S}, mean E = {mean_E}\n")

    return ES_arr, EE_arr


# 下面为输出到文件的一系列主函数
# 调整计算均值的开始位置
def save_step_average(trace, state=0, filename="step_average.txt"):
    ES, EE = analyze_trace_stable(trace, state=state)
    fmt = "%d\t%.8e\t%.8e"
    save_to_file(
        filename, trace["steps"], ES, EE, fmt=fmt, header="Steps,Mean_S,Mean_E"
    )


# 简单地输出 step，S 与 E
def save_SE(trace, tag, state=0):
    fmt = "%d\t%.8e\t%.8e"
    save_to_file(
        f"evol_{tag}.txt",
        trace["steps"],
        trace["S"][state],
        trace["E"][state] / trace["norm"][state],
        fmt=fmt,
        header="Step,S,E",
    )


# 输出块分析的结果
def save_block_energy(trace, tag, state=0):
    std_errs, std_err_errs = block_analysis_energy(
        trace["E"][state], trace["norm"][state]
    )
    n = len(std_errs)
    length = []
    for i in range(n):
        length.append(1 << i)  # 2的i次方
    fmt = "%d\t%.8e\t%.8e"
    save_to_file(
        f"stderr_{tag}.txt",
        length,
        std_errs,
        std_err_errs,
        fmt=fmt,
        header="block_size,std_err,std_err_err",
    )


if __name__ == "__main__":
    # 测试用
    filename = r"trace\block\trace_energy_O16_block_N2LO_opt_hw16_emax8_step140k_Nw1e6_as3_d0.5.txt"
    tag = filename[len(r"trace\block\trace_energy_") : -4]

    num_state = 1
    trace = read_trace_file(filename, num_state)
    save_SE(trace, tag, state=0)
    # save_block_energy(trace, tag, state=0)
