import argparse
import os

from lib.read_file import *
from lib.cal import *
from lib.reweight_tools import *
from lib.estimator import *

""" 
本主函数进行 reweight 计算 S 或 E 的修正，也可以进行块分析
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
        choices=["reweight_s", "reweight_e", "Egr"],
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

    if args.mode == "reweight_e":
        # 计算 E 的重加权量
        input_dtau = 0.0001  # FCIQMC 输入的 dtau
        dtau = compute_dtau(input_dtau)
        order = 1000
        start_idx, W = cal_reweight_factor(
            trace, dtau, order, drop_ratio=args.start, state=args.state
        )
        reweighted_E = cal_reweight_energy(
            trace["E"][args.state], trace["norm"][args.state], start_idx, W
        )
        print(f"Reweighted E (dropping {args.start*100:.1f}%) = {reweighted_E}")

    elif args.mode == "reweight_s":
        # 计算 S 的重加权量
        input_dtau = 0.0001  # FCIQMC 输入的 dtau
        dtau = compute_dtau(input_dtau)
        order = 5000
        reweight_S = cal_reweight_S(
            trace, dtau, order, drop_ratio=args.start, state=args.state
        )
        print(f"Reweighted S (dropping {args.start*100:.1f}%) = {reweight_S}")

    elif args.mode == "Egr":
        # 计算 growth estimator
        input_dtau = 0.0001  # FCIQMC 输入的 dtau
        dtau = compute_dtau(input_dtau)
        Egr = cal_growth_estimator(trace, dtau, drop_ratio=args.start, state=args.state)
        print(f"Growth estimator Egr (dropping {args.start*100:.1f}%) = {Egr}")

    else:
        raise ValueError(f"未知的 mode: {args.mode}")
