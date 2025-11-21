"""
计算模块，在 numpy 内置的函数基础上做一些本程序需要使用的计算
"""

import numpy as np

# 给定一个 idx 计算从这个 idx 到结尾的均值
def cal_mean(start_index, data_array):
    if start_index < 0 or start_index >= len(data_array):
        print(f"Warning: Invalid start index {start_index}.")
        return None
    return np.mean(data_array[start_index:], axis=0)
