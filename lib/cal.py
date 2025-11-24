"""
计算模块，在 numpy 内置的函数基础上做一些本程序需要使用的计算
"""

import numpy as np


# 给定一个索引 start_idx，计算从该索引开始到数组末尾的均值
# 调用的时候输入的是开始的 step，需要找到其在 steps 数组中的索引
def cal_mean(start_idx, data_array):
    if start_idx < 0 or start_idx >= len(data_array):
        raise ValueError("start_idx 超出数据数组范围")
    return np.mean(data_array[start_idx:], axis=0)
