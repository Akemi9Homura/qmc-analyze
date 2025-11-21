import numpy as np


def save_to_file(filename, *arrays, fmt, delimiter=",", header=None):
    """
    将多个NumPy数组作为列写入文件

    参数:
    filename: 输出文件名
    *arrays: 不定数量的NumPy数组（每个数组作为一列）
    delimiter: 列分隔符，默认为逗号
    header: 列标题，可以是列表或字符串
    """

    # 检查是否传入了数组
    if len(arrays) == 0:
        print("错误：至少需要传入一个数组")
        return

    # 检查所有数组长度是否一致
    first_length = len(arrays[0])
    for i, arr in enumerate(arrays):
        if len(arr) != first_length:
            print(
                f"错误：所有数组长度必须相同。第{i+1}个数组长度({len(arr)})与第一个({first_length})不同"
            )
            return

    # 将数组组合成二维数组（每列一个数组）
    combined_data = np.column_stack(arrays)

    # 写入文件
    try:
        np.savetxt(
            filename,
            combined_data,
            fmt=fmt,
            delimiter=delimiter,
            header=header if header else None,
            comments="",
        )  # 不添加注释字符

        print(f"成功将 {len(arrays)} 个数组写入文件: {filename}")
        print(f"文件格式: {combined_data.shape[1]} 列 × {combined_data.shape[0]} 行")

    except Exception as e:
        print(f"写入文件时出错: {e}")
