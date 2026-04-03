import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogLocator, NullFormatter

# ==========================================
# 1. 数据
# ==========================================
E_exact = -20.338832  # 精确解 (MeV)，不需要就设为 None
title = r"$^4$He, N$^2$LO$_\text{opt}$, $\hbar\omega=20$ MeV, $e_\text{max}=2$"
output_name = "He4_N2LO_opt_emax2_Nwconv"
mode = "show"  # "show" 或 "save"

datasets = [
    {
        "Nw": [5e3, 1e4, 5e4, 1e5, 1e6],
        "E": [-20.414074, -20.337607, -20.329052, -20.344092, -20.334321],
        "E_err": [0.037759, 0.037967, 0.015612, 0.009720, 0.004301],
        "label": r"normal FCIQMC",
        "color": "tab:red",
        "fmt": "o-",
    },
    # {
    #     "Nw": [1e3, 1e4, 1e5, 1e6],
    #     "E": [-25.523650, -25.236518, -25.261580, -25.257624],
    #     "E_err": [0.265006, 0.108813, 0.069038, 0.008988],
    #     "label": r"MPI",
    #     "color": "tab:blue",
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
    "legend.fontsize": 20,
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
        label="NCSM",
        zorder=5,
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

plt.xlabel(r"$N_w$")
plt.ylabel(r"$E$ (MeV)")
if title is not None:
    plt.title(title)

ax.legend(frameon=False, loc="best")
plt.tight_layout()

# 图中添加文字
ax.text(
    0.5,
    0.5,
    r"$\text{dimension} = 3060$",
    transform=ax.transAxes,
    fontsize=16,
    verticalalignment="top",
)
ax.text(
    0.5,
    0.4,
    r"$\text{plateau} \approx 1.8\times 10^3$",
    transform=ax.transAxes,
    fontsize=16,
    verticalalignment="top",
)

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
