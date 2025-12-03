import argparse
import os

from lib.read_file import *
from lib.plot import *
from lib.analyze import *
from lib.replica_tools import *

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
        choices=["ee", "ej2", "plot_block_e", "plot_block_j2"],
        help="Which function to run",
    )

    # start / end 用 --start / --end 写，可为 None，由各函数自己判断
    # start 是前百分比
    parser.add_argument("--start", type=float, help="Start step")

    args = parser.parse_args()

    filename = args.file

    log = read_replica_log(filename)

    if args.mode == "ee":
        ee = replica_mean(log["E"], args.start)
        print(f"Replica mean E (dropping {args.start*100:.1f}%) = {ee}")

    elif args.mode == "ej2":
        ej2 = replica_mean(log["J2"], args.start)
        print(f"Replica mean J2 (dropping {args.start*100:.1f}%) = {ej2}")

    elif args.mode == "plotblock_e":
        plot_replica_block(log["E"], args.start)

    elif args.mode == "plot_block_j2":
        plot_replica_block(log["J2"], args.start)

    else:
        raise ValueError(f"未知的 mode: {args.mode}")
