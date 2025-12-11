import argparse
import os

from lib.read_file import *
from lib.plot import *
from lib.analyze import *

""" 
本主函数分析的是一般的 FCIQMC 记录的 trace 文件，是单个 replica 的输出
处理不了 replica 的总 trace 文件
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace analysis tool")

    # 三个位置参数：file, state(可选，默认0), mode
    parser.add_argument("file", help="Path to trace file")
    parser.add_argument(
        "state",
        nargs="?",  # 可选的位置参数
        type=int,
        default=0,  # 不写时 state=0
        help="State index (positional), default=0",
    )
    parser.add_argument(
        "mode",
        choices=["plot", "plotblock", "save_se", "save_block_e", "ee"],
        help="Which function to run",
    )

    # start / end 用 --start / --end 写，可为 None，由各函数自己判断
    parser.add_argument("--start", type=int, help="Start step")
    parser.add_argument("--end", type=int, help="End step")

    args = parser.parse_args()

    filename = args.file
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"文件不存在: {filename}")

    keys = ["trace_energy_", "trace_energy1_", "trace_energy2_"]

    pos = -1
    matched_key = None
    for k in keys:
        pos = filename.find(k)
        if pos != -1:
            matched_key = k
            break

    if matched_key is None:
        raise ValueError(f"未找到{keys}中的任何一个：{filename}")

    tag = os.path.splitext(filename[pos + len(matched_key) :])[0]

    num_state = 1
    trace = read_trace_file(filename, num_state)

    if args.mode == "plot":
        # 画 S 与 E 的演化图到选定的 end 处
        simple_plot_trace(trace, state=args.state, step_end=args.end)

    elif args.mode == "plotblock":
        # 画块分析图
        simple_plot_block(
            trace, state=args.state, step_start=args.start, step_end=args.end
        )

    elif args.mode == "ee":
        # 计算均值，剔除掉 start 之前的数据
        output_mean_energy(trace, state=args.state, step_start=args.start)

    elif args.mode == "save_se":
        # 保存 S 与 E 到文件，范围是 start 到 end
        save_SE_range(
            trace, tag, state=args.state, step_start=args.start, step_end=args.end
        )

    elif args.mode == "save_block_e":
        # 块分析并保存结果到文件，范围是 start 到 end
        save_block_energy(
            trace, tag, state=args.state, step_start=args.start, step_end=args.end
        )

    else:
        raise ValueError(f"未知的 mode: {args.mode}")
