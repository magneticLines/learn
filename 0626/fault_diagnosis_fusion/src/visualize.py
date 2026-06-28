"""可视化：生成报告/PPT 所需的全部图表，保存到 figures/。"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

from mock_sensors import FS, TEMP_LEN, CLASSES

# 中文显示
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 120

_COLORS = ["#2E86AB", "#E1655B", "#F4A259", "#5B8C5A"]


def _ensure(d):
    os.makedirs(d, exist_ok=True)


def plot_waveforms(example_per_class, outdir):
    """各工况振动时域波形（2x2）。"""
    _ensure(outdir)
    t = np.arange(1024) / FS * 1000  # ms，只画前 1024 点更清晰
    fig, axes = plt.subplots(2, 2, figsize=(11, 6))
    for cls, ax in zip(range(4), axes.ravel()):
        sig = example_per_class[cls]["vib"][:1024]
        ax.plot(t, sig, color=_COLORS[cls], lw=0.8)
        ax.set_title(f"{CLASSES[cls]} — 振动时域波形")
        ax.set_xlabel("时间 (ms)")
        ax.set_ylabel("加速度 (g)")
        ax.grid(alpha=0.3)
    fig.suptitle("图 1  四种工况的振动时域波形对比", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(outdir, "fig1_vibration_waveform.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def plot_spectra(example_per_class, outdir):
    """各工况振动频谱，标注故障特征频率。"""
    _ensure(outdir)
    from mock_sensors import BPFO, BPFI, BSF
    fig, axes = plt.subplots(2, 2, figsize=(11, 6))
    for cls, ax in zip(range(4), axes.ravel()):
        sig = example_per_class[cls]["vib"]
        mag = np.abs(rfft(sig))
        freqs = rfftfreq(len(sig), 1 / FS)
        m = freqs <= 1200
        ax.plot(freqs[m], mag[m], color=_COLORS[cls], lw=0.8)
        for f, name, c in [(BPFI, "BPFI", "#d00"), (BPFO, "BPFO", "#090"), (BSF, "BSF", "#06c")]:
            ax.axvline(f, color=c, ls="--", lw=0.8, alpha=0.6)
        ax.set_title(f"{CLASSES[cls]} — 振动频谱")
        ax.set_xlabel("频率 (Hz)")
        ax.set_ylabel("幅值")
        ax.grid(alpha=0.3)
    fig.suptitle("图 2  振动频谱与故障特征频率 (BPFI/BPFO/BSF)", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(outdir, "fig2_vibration_spectrum.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def plot_acoustic_temp(example_per_class, outdir):
    """声学波形 + 温度曲线（上下两行）。"""
    _ensure(outdir)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6))
    t_aco = np.arange(1024) / FS * 1000
    for cls in range(4):
        axes[0].plot(t_aco, example_per_class[cls]["aco"][:1024],
                     color=_COLORS[cls], lw=0.7, alpha=0.8, label=CLASSES[cls])
    axes[0].set_title("各工况声学信号（前 1024 点）")
    axes[0].set_xlabel("时间 (ms)"); axes[0].set_ylabel("声压")
    axes[0].legend(ncol=4, fontsize=9); axes[0].grid(alpha=0.3)

    k = np.arange(TEMP_LEN)
    for cls in range(4):
        axes[1].plot(k, example_per_class[cls]["temp"],
                     color=_COLORS[cls], lw=1.6, marker="o", ms=2, label=CLASSES[cls])
    axes[1].set_title("各工况红外温度曲线")
    axes[1].set_xlabel("时间 (s)"); axes[1].set_ylabel("温度 (°C)")
    axes[1].legend(ncol=4, fontsize=9); axes[1].grid(alpha=0.3)

    fig.suptitle("图 3  声学信号与红外温度对比", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(outdir, "fig3_acoustic_temperature.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def plot_accuracy_comparison(configs, outdir):
    """单传感器 vs 融合 准确率柱状图。"""
    _ensure(outdir)
    names = list(configs.keys())
    accs = [configs[n]["acc"] for n in names]
    colors = ["#9AA0A6", "#9AA0A6", "#9AA0A6", "#E1655B"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, accs, color=colors[:len(names)], width=0.6)
    for b, a in zip(bars, accs):
        ax.text(b.get_x() + b.get_width() / 2, a + 0.01, f"{a:.1%}",
                ha="center", va="bottom", fontweight="bold")
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("故障识别准确率")
    ax.set_title("图 4  单传感器 vs 多传感器融合 准确率对比", fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p = os.path.join(outdir, "fig4_accuracy_comparison.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def plot_confusion_matrices(configs, classes, outdir):
    """四个配置的混淆矩阵（2x2）。"""
    _ensure(outdir)
    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    for (name, c), ax in zip(configs.items(), axes.ravel()):
        cm = c["cm"]
        im = ax.imshow(cm, cmap="Blues")
        ax.set_title(f"{name}  (acc={c['acc']:.1%})")
        ax.set_xticks(range(len(classes))); ax.set_yticks(range(len(classes)))
        ax.set_xticklabels(classes, rotation=30, ha="right", fontsize=8)
        ax.set_yticklabels(classes, fontsize=8)
        ax.set_xlabel("预测"); ax.set_ylabel("真实")
        thr = cm.max() / 2
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, int(cm[i, j]), ha="center", va="center",
                        color="white" if cm[i, j] > thr else "black", fontsize=9)
    fig.suptitle("图 5  各配置混淆矩阵", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(outdir, "fig5_confusion_matrices.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def plot_feature_importance(fused_importance, outdir, top=10):
    """融合模型特征重要性（按传感器着色）。"""
    _ensure(outdir)
    items = fused_importance[:top][::-1]
    names = [n for n, _ in items]
    vals = [v for _, v in items]
    cmap = {"vib": "#2E86AB", "aco": "#F4A259", "temp": "#5B8C5A"}
    colors = [cmap[n.split("_")[0]] for n in names]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(names, vals, color=colors)
    ax.set_xlabel("重要性")
    ax.set_title(f"图 6  融合模型 Top-{top} 特征重要性", fontsize=13, fontweight="bold")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=cmap["vib"], label="振动"),
                       Patch(color=cmap["aco"], label="声学"),
                       Patch(color=cmap["temp"], label="温度")], fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    p = os.path.join(outdir, "fig6_feature_importance.png")
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p
