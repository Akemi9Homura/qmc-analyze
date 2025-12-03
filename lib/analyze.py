from .write_file import *
from .cal import *
from .block import *

# --- 最终执行操作的主函数 --


# 把全部的 step，S 与 E 保存到文件
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


# 把给定 step 起止范围的 S 与 E 保存到文件
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


# 输出从给定起始位置到末尾的均值
def output_mean_energy(trace, state=0, step_start=None):
    if step_start is not None:
        start_index = np.searchsorted(trace["steps"], step_start, side="left")
        if (
            start_index >= len(trace["steps"])
            or trace["steps"][start_index] != step_start
        ):
            raise ValueError(f"未找到 step_start = {step_start}")
    else:
        start_index = 0

    mean_energy = cal_mean(start_index, trace["E"][state] / trace["norm"][state])
    print(f"Mean energy (state={state}, step_start={step_start}): {mean_energy}")


# 块分析的结果保存到文件
def save_block_energy(trace, tag, state=0, step_start=None, step_end=None):
    # 从 steps 中找到 start_point 对应的索引
    if step_start is None:
        start_index = 0
    else:
        start_index = np.searchsorted(trace["steps"], step_start, side="left")
        if (
            start_index >= len(trace["steps"])
            or trace["steps"][start_index] != step_start
        ):
            raise ValueError(f"未找到 step_start = {step_start}")
    if step_end is None:
        end_index = len(trace["steps"])
    else:
        end_index = np.searchsorted(trace["steps"], step_end, side="right")
        if end_index == 0 or trace["steps"][end_index - 1] != step_end:
            raise ValueError(f"未找到 step_end = {step_end}")

    std_errs, std_err_errs = block_analysis_energy(
        trace["E"][state][start_index:end_index],
        trace["norm"][state][start_index:end_index],
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
