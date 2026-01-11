import matplotlib.pyplot as plt
import numpy as np
from lib.read_file import *
from lib.reweight_tools import compute_dtau

# ==========================================
# 1. 数据
# ==========================================
filename = r"d:\My work\FCIQMC\statistics\result\Be8\trace_energy_Be8_cut0.1_N2LO_opt_hw20_emax2_step50k_Nw5e5_n.txt"
trace, type = read_trace_auto(filename)

# 设置参数
state = 0  # 要画的态
exact_energy = -26.325446  # 精确解 (MeV)
dtau = 1e-4
dtau = compute_dtau(dtau)

# 提取数据
S_data = trace["S"][state]
E_data = trace["E"][state]
norm_data = trace["norm"][state]
times = trace["steps"] * dtau

# 防止除以0警告
with np.errstate(divide="ignore", invalid="ignore"):
    Enorm_data = E_data / norm_data

# ==========================================
# 2. 绘图配置
# ==========================================
# 全局字体与大小设置
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.size"] = 18
config = {
    # 刻度线设置
    ## 方向
    "xtick.direction": "in",  # X轴刻度朝里
    "ytick.direction": "in",  # Y轴刻度朝里
    "xtick.top": True,  # 上方显示刻度
    "ytick.right": True,  # 右方显示刻度
    ## 粗细
    "axes.linewidth": 1.5,  # 边框线宽
    "xtick.major.width": 1.5,  # X 轴刻度线粗细
    "ytick.major.width": 1.5,  # Y 轴刻度线粗细
    "xtick.major.size": 10.0,  # (可选) 刻度线长度稍微加长一点更美观
    "ytick.major.size": 10.0,
    ## 次刻度线
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "xtick.minor.width": 1.0,
    "ytick.minor.width": 1.0,
    "xtick.minor.size": 5.0,
    "ytick.minor.size": 5.0,
    # 字体大小设置
    "axes.labelsize": 20,  # 【重点】横纵轴“名称”的大小
    "xtick.labelsize": 20,  # 【重点】横轴“刻度数字”的大小
    "ytick.labelsize": 20,  # 【重点】纵轴“刻度数字”的大小
    "legend.fontsize": 20,  # 图例字体大小
}
plt.rcParams.update(config)

# ==========================================
# 3. 开始绘图
# ==========================================
plt.figure(figsize=(8, 6))

# 绘制 S (绿色)
plt.plot(times, S_data, label=r"$S$", color="tab:green", linewidth=1.5, alpha=0.8)

# 绘制 Energy (红色)
plt.plot(
    times,
    Enorm_data,
    label=r"$E$",
    color="tab:red",
    linewidth=1.5,
)

# 绘制精确解 (黑色虚线)
# zorder设为10确保它画在最上层，或者设为1画在背景层
plt.axhline(
    y=exact_energy,
    color="black",
    linestyle="--",
    linewidth=2,
    label=r"NCSM",
    zorder=5,
)

# ==========================================
# 4. 标签与修饰
# ==========================================
plt.xlabel(r"$\tau$ (zs)")
plt.ylabel(r"$E$ (MeV)")  # 因为共用轴，单位可能不统一，这里写 Value 或根据情况修改
plt.title(r"$^8$Be, N$^2$LO$_\text{opt}$, $\hbar\omega=20$ MeV, $e_\text{max}=2$")

# 轴范围
plt.xlim(right=8)
plt.ylim(top=-5)

# 图例 (去掉边框更简洁)
plt.legend(frameon=False, loc="best")

# 自动调整布局防止遮挡
plt.tight_layout()

# 显示图片
# plt.show()
# 保存图片
plt.savefig("trace_plot.pdf", bbox_inches="tight")
