import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, NullFormatter
from matplotlib.transforms import blended_transform_factory

# ==========================================
# 1. 数据
# ==========================================
E_exact = -87.104449  # 精确解 (MeV)，不需要就设为 None
title = r"$^{24}$Mg, USDB"
output_name = "Mg24_USDB_as_Nwconv"
mode = "show"  # "show" 或 "save"

datasets = [
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-83.155075, -84.748835, -85.696193, -86.992861, -87.058679],
        "E_err": [0.038018, 0.047494, 0.053479, 0.029766, 0.047259],
        "label": r"normal initiator",
        "color": "tab:cyan",
        "fmt": "s--",
    },
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-84.052928, -85.674163, -86.562924, -87.131397, -87.086961],
        "E_err": [0.048269, 0.064248, 0.051015, 0.025993, 0.014237],
        "label": r"$\Delta=0.5$",
        "color": "tab:green",
        "fmt": "s-",
    },
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-84.853691, -86.377999, -87.042250, -87.230619, -87.114738],
        "E_err": [0.070854, 0.055334, 0.052584, 0.032560, 0.040383],
        "label": r"$\Delta=0.2$",
        "color": "tab:olive",
        "fmt": "s-",
    },
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-85.390462, -86.911872, -87.063606, -87.083116, -87.097005],
        "E_err": [0.154909, 0.090890, 0.088253, 0.028915, 0.018603],
        "label": r"$\Delta=0.1$",
        "color": "tab:brown",
        "fmt": "s-",
    },
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-85.940409, -87.286966, -87.404418, -87.194839, -87.134792],
        "E_err": [0.118156, 0.105993, 0.063078, 0.031656, 0.021762],
        "label": r"$\Delta=0$",
        "color": "tab:orange",
        "fmt": "o-",
    },
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-86.729205, -87.575427, -87.542187, -87.170010, -87.101677],
        "E_err": [0.116646, 0.081947, 0.074018, 0.029968, 0.017136],
        "label": r"$\Delta=-0.1$",
        "color": "tab:blue",
        "fmt": "s-",
    },
    {
        "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
        "E": [-87.739480, -87.949175, -87.761729, -87.109748, -87.133592],
        "E_err": [0.133025, 0.126710, 0.065572, 0.029827, 0.029629],
        "label": r"$\Delta=-0.2$",
        "color": "tab:purple",
        "fmt": "s-",
    },
    # {
    #     "Nw": [1e3, 5e3, 1e4, 5e4, 1e5],
    #     "E": [-92.422889, -89.390912, -88.362046, -87.181605, -87.119271],
    #     "E_err": [0.115339, 0.111314, 0.051155, 0.039317, 0.018922],
    #     "label": r"$\Delta=-0.5$",
    #     "color": "tab:red",
    #     "fmt": "s-",
    # },
    # 继续添加更多线 ...
]

# ==========================================
# 2. 绘图配置
# ==========================================
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.size"] = 18
config = {
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "axes.linewidth": 1.5,
    "xtick.major.width": 1.5,
    "ytick.major.width": 1.5,
    "xtick.major.size": 10.0,
    "ytick.major.size": 10.0,
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "xtick.minor.width": 1.0,
    "ytick.minor.width": 1.0,
    "xtick.minor.size": 5.0,
    "ytick.minor.size": 5.0,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 16,
}
plt.rcParams.update(config)

# ==========================================
# 3. 开始绘图
# ==========================================
plt.figure(figsize=(8, 6))

for ds in datasets:
    yerr = np.asarray(ds["E_err"], dtype=float) if ds["E_err"] else None
    plt.errorbar(
        np.asarray(ds["Nw"], dtype=float),
        np.asarray(ds["E"], dtype=float),
        yerr=yerr,
        fmt=ds["fmt"],
        color=ds["color"],
        capsize=5,
        linewidth=1.5,
        markersize=6,
        label=ds["label"],
    )

# 严格解水平线
if E_exact is not None:
    plt.axhline(
        y=E_exact,
        color="black",
        linestyle="--",
        linewidth=2,
        # label="NCSM",
        zorder=5,
    )
    trans = blended_transform_factory(plt.gca().transAxes, plt.gca().transData)
    plt.gca().text(
        0.85,
        E_exact - 0.5,
        "NCSM",
        fontsize=18,
        ha="left",
        va="bottom",
        transform=trans,
    )

# ==========================================
# 4. 标签与修饰
# ==========================================
plt.xscale("log")

# 次刻度只在 5×10^n 处
ax = plt.gca()

# ax.set_xlim(left=1e3)

ax.xaxis.set_minor_locator(LogLocator(subs=(5,), numticks=10))
ax.xaxis.set_minor_formatter(NullFormatter())

# 刻度标签往外推，不那么拥挤
ax.tick_params(axis="x", which="major", pad=8)
ax.tick_params(axis="y", which="major", pad=5)

# ax.set_ylim(-180, -120)

plt.xlabel(r"$N_w$")
plt.ylabel(r"$E$ (MeV)")
if title is not None:
    plt.title(title)

ax.legend(frameon=False, loc="upper right")
plt.tight_layout()

# 图中添加文字
# ax.text(
#     0.5,
#     0.2,
#     r"$\text{dimension} = 3060$",
#     transform=ax.transAxes,
#     fontsize=16,
#     verticalalignment="top",
# )
# ax.text(
#     0.5,
#     0.3,
#     r"$\text{plateau} \approx 1.8\times 10^3$",
#     transform=ax.transAxes,
#     fontsize=16,
#     verticalalignment="top",
# )

# ==========================================
# 5. 输出
# ==========================================
if mode == "show":
    plt.show()
elif mode == "save":
    plt.savefig(f"{output_name}.pdf", bbox_inches="tight")
    plt.close()
    with open(f"{output_name}.txt", "w") as f:
        f.write(f"# title: {title}\n")
        f.write(f"# E_exact (MeV): {E_exact}\n\n")
        for ds in datasets:
            f.write(f"# --- {ds['label']} ---\n")
            f.write(f"Nw_list    = {ds['Nw']}\n")
            f.write(f"E_list     = {ds['E']}\n")
            f.write(f"E_err_list = {ds['E_err']}\n\n")
    print(f"已保存图片：{output_name}.pdf")
    print(f"已保存数据：{output_name}.txt")
else:
    raise ValueError(f"mode 必须是 'show' 或 'save'，当前值为 '{mode}'")
