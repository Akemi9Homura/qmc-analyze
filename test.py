from lib.read_file import *


# 还是直接输入 numpy 数组更好，现在这样太具体了
# 给定开始位置，计算开始位置到结束的均值
def cal_mean_test(start_index, data_array):
    if start_index < 0 or start_index >= len(data_array):
        print(f"Warning: Invalid start index {start_index}.")
        return None
    return np.mean(data_array[start_index:], axis=0)


if __name__ == "__main__":
    # 使用原始字符串（在字符串前加r），避免\t被解释为制表符
    filename = (
        r"trace\trace_energy_O16_asmod2_N2LO_opt_hw16_emax8_step4k_Nw1e5_as3_d0.5.txt"
    )

    trace = read_trace_file(filename)
    print(f"采样了 {len(trace['steps'])} 组数据")

    state_idx = 0
    start_idx = 2
    if start_idx >= len(trace["steps"]):
        print(
            f"Warning: start index {start_idx} exceeds number of steps {len(trace['steps'])}."
        )
        sys.exit(1)
    start_step = trace["steps"][start_idx]
    Smean = cal_mean_test(start_idx, trace["S"][state_idx])
    Emean = cal_mean_test(start_idx, trace["E"][state_idx])
    J2mean = cal_mean_test(start_idx, trace["J2"][state_idx])
    normmean = cal_mean_test(start_idx, trace["norm"][state_idx])
    print(
        f"从第 {start_step} 步开始计算均值: \n"
        f"S = {Smean}, E = {Emean/normmean}, J2 = {J2mean/normmean}"
    )
