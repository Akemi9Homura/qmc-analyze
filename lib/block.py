"""
定义块分析需要的函数
"""

import numpy as np

# X/Y 标准差合成
def std_err_ratio(X_mean, Y_mean, X_std_err, Y_std_err, cov_XY, data_num):
    ratio_mean = X_mean / Y_mean
    ratio_std_err = abs(
        ratio_mean
        * np.sqrt(
            (X_std_err / X_mean) ** 2
            + (Y_std_err / Y_mean) ** 2
            - 2 * cov_XY / (data_num * X_mean * Y_mean)
        )
    )
    return ratio_std_err


# 单个 array 的块分析
def block_analysis(array, ddof=1):
    data_num = len(array)
    i = 0
    std_errs = []
    std_err_errs = []
    print("Starting block analysis for energy...")
    # 循环直到2^i大于数据总量
    while True:
        block_size = 1 << i
        # 如果块大小大于数据总量，结束循环
        if block_size > data_num:
            break

        # 计算余数（开头不完整的数据量）
        remainder = data_num % block_size

        # 如果余数为0，说明数据可以完全分块
        if remainder == 0:
            # 所有数据都参与计算
            start_idx = 0
            num_blocks = data_num // block_size
        else:
            # 跳过开头不完整的数据
            start_idx = remainder
            num_blocks = (data_num - remainder) // block_size

        # 如果块数量小于等于 ddof，分母的 n-ddof 就不对了，此时停止计算
        if num_blocks <= ddof:
            break

        print(f"i = {i}, block size = {block_size}")
        # 每个 block 求数据的均值
        mean_block = []
        for j in range(num_blocks):
            # 计算当前块的起始和结束索引
            current_start = start_idx + j * block_size
            current_end = current_start + block_size

            # 计算当前块的均值并存起来
            mean = np.mean(array[current_start:current_end])
            mean_block.append(mean)

        mean = np.mean(mean_block)
        std_err = np.std(mean_block, ddof=ddof) / np.sqrt(num_blocks)
        std_err_err = std_err / np.sqrt(2 * (num_blocks - ddof))
        std_errs.append(std_err)
        std_err_errs.append(std_err_err)

        i += 1  # 增加块大小指数

    return std_errs, std_err_errs


# 块分析能量，需要输入未归一化的能量与归一化因子
def block_analysis_energy(E_array, norm_array, ddof=1):
    # 检查
    if len(E_array) != len(norm_array):
        print("Error: E_array and norm_array must have the same length.")
        return None, None

    data_num = len(E_array)
    i = 0
    std_errs = []
    std_err_errs = []
    print("Starting block analysis for energy...")
    # 循环直到2^i大于数据总量
    while True:
        block_size = 1 << i
        # 如果块大小大于数据总量，结束循环
        if block_size > data_num:
            break

        # 计算余数（开头不完整的数据量）
        remainder = data_num % block_size

        # 如果余数为0，说明数据可以完全分块
        if remainder == 0:
            # 所有数据都参与计算
            start_idx = 0
            num_blocks = data_num // block_size
        else:
            # 跳过开头不完整的数据
            start_idx = remainder
            num_blocks = (data_num - remainder) // block_size

        # 如果块数量小于等于 ddof，分母的 n-ddof 就不对了，此时停止计算
        if num_blocks <= ddof:
            break

        print(f"i = {i}, block size = {block_size}")
        # 每个 block 求数据的均值
        Emean_block = []
        normmean_block = []
        for j in range(num_blocks):
            # 计算当前块的起始和结束索引
            current_start = start_idx + j * block_size
            current_end = current_start + block_size

            # 计算当前块的均值并存起来
            Emean = np.mean(E_array[current_start:current_end])
            normmean = np.mean(norm_array[current_start:current_end])
            Emean_block.append(Emean)
            normmean_block.append(normmean)

        Emean = np.mean(Emean_block)
        normmean = np.mean(normmean_block)
        E_std_str = np.std(Emean_block, ddof=ddof) / np.sqrt(num_blocks)
        norm_std_str = np.std(normmean_block, ddof=ddof) / np.sqrt(num_blocks)
        cov_EN = np.cov(Emean_block, normmean_block, ddof=ddof)[0, 1]
        std_err = std_err_ratio(
            Emean,
            normmean,
            E_std_str,
            norm_std_str,
            cov_EN,
            num_blocks,
        )
        std_err_err = std_err / np.sqrt(2 * (num_blocks - ddof))
        std_errs.append(std_err)
        std_err_errs.append(std_err_err)

        i += 1  # 增加块大小指数

    return std_errs, std_err_errs
