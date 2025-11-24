"""
主函数中定义的函数输入量全都是 trace，需要具体处理特定的数据结构
而不具体到 trace 结构的函数则放在 cal.py 中
"""

from lib.read_file import *
from lib.write_file import *
from lib.cal import *
from lib.block import *
from lib.plot import *

import argparse
import os

# 绘制演化图的函数
# 简单地输出全部的 step，S 与 E
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
    
# 输出给定 step 起止范围的 S 与 E
def save_SE_range(trace, tag, state=0, step_start=None, step_end=None):
    steps = trace["steps"]
    S_values = trace["S"][state]
    E_values = trace["E"][state] / trace["norm"][state]
        
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

    # 筛选出指定范围内的步数及对应的 S 和 E
    selected_steps = steps[start_index:end_index]
    selected_S = S_values[start_index:end_index]
    selected_E = E_values[start_index:end_index]

    fmt = "%d\t%.8e\t%.8e"
    save_to_file(
        f"evol_{tag}_range_{step_start}_{step_end}.txt",
        selected_steps,
        selected_S,
        selected_E,
        fmt=fmt,
        header="Step,S,E",
    )


# 计算均值的函数
def output_mean_energy(trace, state=0, step_start=None):
    if step_start is not None:
        start_index = np.searchsorted(trace["steps"], step_start, side="left")
        if start_index >= len(trace["steps"]) or trace["steps"][start_index] != step_start:
            raise ValueError(f"未找到 step_start = {step_start}")
    else:
        start_index = 0

    mean_energy = cal_mean(start_index, trace["E"][state]/trace["norm"][state])
    print(f"Mean energy (state={state}, step_start={step_start}): {mean_energy}")


# 块分析标准差
# 使用 trace 中的所有数据，不截断任何东西
def save_block_energy_all(trace, tag, state=0):
    # 从 steps 中找到 start_point 对应的索引
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
    
# 设置计算的起止 step
def save_block_energy(trace, tag, state=0, step_start=None, step_end=None):
    # 从 steps 中找到 start_point 对应的索引
    if step_start is None:
        start_index = 0
    else:
        start_index = np.searchsorted(trace["steps"], step_start, side="left")
        if start_index >= len(trace["steps"]) or trace["steps"][start_index] != step_start:
            raise ValueError(f"未找到 step_start = {step_start}")
    if step_end is None:
        end_index = len(trace["steps"])
    else:
        end_index = np.searchsorted(trace["steps"], step_end, side="right")
        if end_index == 0 or trace["steps"][end_index - 1] != step_end:
            raise ValueError(f"未找到 step_end = {step_end}")

    std_errs, std_err_errs = block_analysis_energy(
        trace["E"][state][start_index:end_index], trace["norm"][state][start_index:end_index]
    )
    n = len(std_errs)
    length = []
    for i in range(n):
        length.append(1 << i)  # 2的i次方
    fmt = "%d\t%.8e\t%.8e"
    filename_tag = tag
    if step_start is not None:
        filename_tag = f"{filename_tag}_start{step_start}"
    if step_end is not None:
        filename_tag = f"{filename_tag}_end{step_end}"
    save_to_file(
        f"stderr_{filename_tag}.txt",
        length,
        std_errs,
        std_err_errs,
        fmt=fmt,
        header="block_size,std_err,std_err_err",
    )


# 主函数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace analysis tool")

    parser.add_argument("--file", required=True, help="Path to trace file")
    parser.add_argument("--mode", required=True,
                        choices=["plot_se", "plot_block", "save_se", "save_block_e", "mean_energy"],
                        help="Which function to run")

    parser.add_argument("--state", type=int, default=0, help="State index, default=0")
    parser.add_argument("--start", type=int, help="Start step")
    parser.add_argument("--end", type=int, help="End step")

    args = parser.parse_args()
    
    filename = args.file
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"文件不存在: {filename}")
    
    key = "trace_energy_"
    pos = filename.find(key)
    if pos == -1:
        raise ValueError(f"未找到'{key}'：{filename}")
    tag = os.path.splitext(filename[pos + len(key):])[0]

    # 默认 num_state = 1
    num_state = 1
    trace = read_trace_file(filename, num_state)
    
    # 画 S 与 E 的演化图到选定的 end 处
    if args.mode == "plot_se":
        simple_plot_trace(trace, state=args.state, end=args.end)

    # 画块分析图，范围是输入的 start 到 end
    if args.mode == "plot_block":
        simple_plot_block(trace, state=args.state, step_start=args.start, step_end=args.end)
        
    # 计算均值，剔除掉 start 之前的数据
    if args.mode == "mean_energy":
        output_mean_energy(trace, state=args.state, step_start=args.start)
        
    # 保存 S 与 E 到文件
    if args.mode == "save_se":
        save_SE_range(trace, tag, state=args.state, step_start=args.start, step_end=args.end)
    # 块分析并保存结果到文件
    if args.mode == "save_block_e":
        save_block_energy(trace, tag, state=args.state, step_start=args.start, step_end=args.end)
