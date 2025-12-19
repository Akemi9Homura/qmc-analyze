import argparse
import os

from lib.read_file import *
from lib.plot import *
from lib.cal import *

""" 
本主函数分析的是 trace 文件，trace 文件有两种，均支持
一种是 replica 的总 trace 文件，文件头是 # i, replica_E, replica_J2, norm
另一种是非 replica 的，或 replica 中每个单独记录的，文件头是 # i, Nw, S, E, J2, norm
根据文件头选择读取哪一种
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log analysis tool")

    # 三个位置参数：file, state(可选，默认0), mode
    parser.add_argument("file", help="Path to log file")
    parser.add_argument(
        "state",
        nargs="?",  # 可选的位置参数
        type=int,
        default=0,  # 不写时 state=0
        help="State index (positional), default=0",
    )
    parser.add_argument(
        "mode",
        choices=[
            "es",
            "ee",
            "ej2",
            "plot_evol",
            "plot_block_e",
            "plot_block_se",
            "testlog",
        ],  # 暂时不写 J2 的块分析
        help="Which function to run",
    )

    # start 不是位置参数，因为有 --，用 --start 写，可以不提供
    # 而位置参数必须提供
    parser.add_argument("--start", type=float, default=0.3, help="Start step")

    args = parser.parse_args()

    filename = args.file
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"文件不存在: {filename}")

    trace, type = read_trace_auto(filename)
    is_replica = type == "replica"

    if args.mode == "es":
        # 计算 S 的平均值
        if is_replica:
            raise ValueError("replica trace 文件中没有 S 数据，无法计算平均 S")
        es = cal_mean(trace["S"][args.state], drop_ratio=args.start)
        print(f"Mean S (dropping {args.start*100:.1f}%) = {es}")

    elif args.mode == "ee":
        # 计算 E 均值除以 norm 均值
        ee = cal_mean(trace["E"][args.state], drop_ratio=args.start)
        enorm = cal_mean(trace["norm"][args.state], drop_ratio=args.start)
        print(f"Mean E (dropping {args.start*100:.1f}%) = {ee/enorm}")

    elif args.mode == "ej2":
        # 计算 J2 均值除以 norm 均值
        ej2 = cal_mean(trace["J2"][args.state], drop_ratio=args.start)
        enorm = cal_mean(trace["norm"][args.state], drop_ratio=args.start)
        print(f"Mean J2 (dropping {args.start*100:.1f}%) = {ej2 / enorm}")

    elif args.mode == "plot_evol":
        # 画演化图
        if is_replica:
            raise ValueError("replica trace 文件无法画演化图")
        plot_trace(trace, state=args.state)

    elif args.mode == "plot_block_e":
        # 只画 E 的块分析图
        plot_block_e(trace, drop_ratio=args.start, state=args.state)

    elif args.mode == "plot_block_se":
        # 画 S 与 E 的块分析图
        if is_replica:
            raise ValueError("replica trace 文件中没有 S 数据，无法画 S 的块分析图")
        plot_block_se(trace, drop_ratio=args.start, state=args.state)

    elif args.mode == "testlog":
        # 与处理 log 的函数比较，检查可能的错误
        ee = cal_mean(
            trace["E"][args.state] / trace["norm"][args.state], drop_ratio=args.start
        )
        ej2 = cal_mean(
            trace["J2"][args.state] / trace["norm"][args.state], drop_ratio=args.start
        )
        print(f"Mean E (dropping {args.start*100:.1f}%) = {ee}")
        print(f"Mean J2 (dropping {args.start*100:.1f}%) = {ej2}")

    else:
        raise ValueError(f"未知的 mode: {args.mode}")
