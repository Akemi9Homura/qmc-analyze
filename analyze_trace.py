import argparse
import os
import sys
import numpy as np

from lib.read_file import *
from lib.plot import *
from lib.cal import *

""" 
本代码分析 trace 文件，trace 文件有两种，均支持
一种是 replica 的总 trace 文件，文件头是 # i, replica_E, replica_J2, norm
另一种是非 replica 的，或 replica 中每个单独记录的，文件头是 # i, Nw, S, E, J2, norm
根据文件头选择读取哪一种，replica 的现在不用了，需要修改
"""

if __name__ == "__main__":
    # 如果最后一个参数不在 choices 里，说明 mode 没有提供，手动补上 "all"
    _choices = {
        "es",
        "ee",
        "ej2",
        "plot",
        "plot_block_e",
        "plot_block_se",
        "all",
        "testlog",
    }
    if len(sys.argv) >= 2 and sys.argv[-1] not in _choices:
        sys.argv.append("all")

    parser = argparse.ArgumentParser(description="Log analysis tool")

    # 位置参数：file, mode
    parser.add_argument("file", help="Path to log file")
    parser.add_argument(
        "mode",
        choices=[
            "es",
            "ee",
            "ej2",
            "plot",
            "plot_block_e",
            "plot_block_se",
            "all",
            "testlog",
        ],
        help="Which function to run (default: all)",
    )

    # 选项参数：--state, --start
    parser.add_argument("--state", type=int, default=0, help="State index, default=0")
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
        print(f"Mean S (dropping {args.start*100:.1f}%) = {es:.6f}")

    elif args.mode == "ee":
        # 计算 E 均值除以 norm 均值
        ee = cal_mean(trace["E"][args.state], drop_ratio=args.start)
        enorm = cal_mean(trace["norm"][args.state], drop_ratio=args.start)
        print(f"Mean E (dropping {args.start*100:.1f}%) = {ee/enorm:.6f}")

    elif args.mode == "ej2":
        # 计算 J2 均值除以 norm 均值
        ej2 = cal_mean(trace["J2"][args.state], drop_ratio=args.start)
        enorm = cal_mean(trace["norm"][args.state], drop_ratio=args.start)
        print(f"Mean J2 (dropping {args.start*100:.1f}%) = {ej2 / enorm:.6f}")

    elif args.mode == "plot":
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

    elif args.mode == "all":
        if is_replica:
            raise ValueError("replica trace 文件不支持 all 分析")

        E_arr = np.asarray(trace["E"][args.state], dtype=float)
        norm_arr = np.asarray(trace["norm"][args.state], dtype=float)
        S_arr = np.asarray(trace["S"][args.state], dtype=float)

        n = E_arr.size
        drop_n = int(n * args.start)

        E_seg = E_arr[drop_n:]
        norm_seg = norm_arr[drop_n:]
        S_seg = S_arr[drop_n:]

        # 中心值
        s_mean = np.mean(S_seg)
        e_mean = np.mean(E_seg) / np.mean(norm_seg)

        # 各自的块分析
        std_errs_E, std_err_errs_E = block_analysis_energy(E_seg, norm_seg)
        std_errs_S, std_err_errs_S = block_analysis(S_seg)

        sigma_e = get_block_std_err_max(std_errs_E, std_err_errs_E)
        sigma_s = get_block_std_err_max(std_errs_S, std_err_errs_S)

        print(f"S (dropping {args.start*100:.1f}%): {s_mean:.6f} ± {sigma_s:.6f}")
        print(f"E (dropping {args.start*100:.1f}%): {e_mean:.6f} ± {sigma_e:.6f}")

        # 对差值序列做块分析，自动包含协方差
        # 这是为了验证 S 与 E 收敛到同一值，否则演化还不够
        delta_seg = S_seg - E_seg / norm_seg
        std_errs_D, std_err_errs_D = block_analysis(delta_seg)
        sigma_d = get_block_std_err_max(std_errs_D, std_err_errs_D)
        delta_mean = np.mean(delta_seg)

        n_sigma = abs(delta_mean) / sigma_d
        if n_sigma <= 1:
            print(
                f"S 与 E 一致: Δ = {delta_mean:.6f} ± {sigma_d:.6f} ({n_sigma:.2f}σ)"
            )
        elif n_sigma <= 2:
            print(
                f"S 与 E 轻微偏差: Δ = {delta_mean:.6f} ± {sigma_d:.6f} ({n_sigma:.2f}σ)"
            )
        elif n_sigma <= 3:
            print(
                f"警告，S 与 E 大偏差，演化未收敛: Δ = {delta_mean:.6f} ± {sigma_d:.6f} ({n_sigma:.2f}σ)"
            )
        else:
            print(
                f"错误，S 与 E 不一致，演化未收敛: Δ = {delta_mean:.6f} ± {sigma_d:.6f} ({n_sigma:.2f}σ)"
            )

    elif args.mode == "testlog":
        # 与处理 log 的函数比较，检查可能的错误
        ee = cal_mean(
            trace["E"][args.state] / trace["norm"][args.state], drop_ratio=args.start
        )
        ej2 = cal_mean(
            trace["J2"][args.state] / trace["norm"][args.state], drop_ratio=args.start
        )
        print(f"Mean E (dropping {args.start*100:.1f}%) = {ee:.6f}")
        print(f"Mean J2 (dropping {args.start*100:.1f}%) = {ej2:.6f}")

    else:
        raise ValueError(f"未知的 mode: {args.mode}")
