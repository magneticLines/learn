"""交互式演示（用于录制演示视频）。

启动后训练一次三传感器融合模型，然后：
  - 点击「随机诊断一个样本」按钮，抽取一个随机工况样本；
  - 动画绘制振动 / 声学 / 温度三路信号；
  - 顶部显示「真实工况」与「融合模型诊断结果」，正确为绿色、错误为红色。

运行：
    python demo/demo.py
"""
import os
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mock_sensors import generate_dataset, generate_sample, FS, TEMP_LEN, CLASSES
from features import build_matrix, extract_all
from sklearn.ensemble import RandomForestClassifier

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = ["#2E86AB", "#E1655B", "#F4A259", "#5B8C5A"]


def train_model():
    samples, _ = generate_dataset(n_per_class=200, seed=42)
    X, y, names, sensors = build_matrix(samples)
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X, y)
    return clf, names


class Demo:
    def __init__(self):
        print("训练三传感器融合模型 ...")
        self.clf, self.feature_names = train_model()
        self.rng = np.random.default_rng()

        self.fig, self.axes = plt.subplots(3, 1, figsize=(10, 7))
        self.fig.subplots_adjust(bottom=0.16, top=0.88, hspace=0.5)
        self.fig.suptitle("多传感器融合故障诊断 — 实时演示", fontsize=14, fontweight="bold")

        ax_btn = self.fig.add_axes([0.4, 0.04, 0.2, 0.06])
        self.btn = Button(ax_btn, "随机诊断一个样本", color="#E1655B", hovercolor="#c94f45")
        self.btn.label.set_color("white")
        self.btn.on_clicked(self.on_click)

        self.anim = None
        self.sample_once()

    def sample_once(self):
        cls = int(self.rng.integers(0, len(CLASSES)))
        self.sample = generate_sample(cls, self.rng)
        f = extract_all(self.sample)
        x = np.array([[f[k] for k in self.feature_names]])
        self.pred = int(self.clf.predict(x)[0])
        self.true = cls
        self.draw()

    def draw(self):
        for ax in self.axes:
            ax.clear()
        ok = self.pred == self.true
        color = "#1a7f37" if ok else "#d1242f"
        mark = "✓ 诊断正确" if ok else "✗ 诊断错误"
        self.fig.suptitle(
            f"真实工况：{CLASSES[self.true]}    |    融合诊断：{CLASSES[self.pred]}    {mark}",
            fontsize=14, fontweight="bold", color=color,
        )

        t = np.arange(1024) / FS * 1000
        vib = self.sample["vib"][:1024]
        aco = self.sample["aco"][:1024]
        temp = self.sample["temp"]

        self.axes[0].set_title("振动传感器（加速度）")
        self.axes[0].set_xlim(0, t[-1]); self.axes[0].set_ylim(vib.min() * 1.1, vib.max() * 1.1)
        self.axes[0].set_xlabel("时间 (ms)"); self.axes[0].grid(alpha=0.3)
        (self.l_vib,) = self.axes[0].plot([], [], color=COLORS[0], lw=0.8)

        self.axes[1].set_title("声学麦克风（声压）")
        self.axes[1].set_xlim(0, t[-1]); self.axes[1].set_ylim(aco.min() * 1.1, aco.max() * 1.1)
        self.axes[1].set_xlabel("时间 (ms)"); self.axes[1].grid(alpha=0.3)
        (self.l_aco,) = self.axes[1].plot([], [], color=COLORS[2], lw=0.7)

        self.axes[2].set_title("红外温度（°C）")
        self.axes[2].set_xlim(0, TEMP_LEN - 1); self.axes[2].set_ylim(temp.min() - 2, temp.max() + 2)
        self.axes[2].set_xlabel("时间 (s)"); self.axes[2].grid(alpha=0.3)
        (self.l_temp,) = self.axes[2].plot([], [], color=COLORS[3], lw=1.6, marker="o", ms=2)

        self._t, self._vib, self._aco, self._temp = t, vib, aco, temp
        if self.anim is not None:
            self.anim.event_source.stop()
        self.anim = FuncAnimation(self.fig, self._update, frames=40,
                                  interval=30, blit=False, repeat=False)
        self.fig.canvas.draw_idle()

    def _update(self, frame):
        n = int((frame + 1) / 40 * 1024)
        m = int((frame + 1) / 40 * TEMP_LEN)
        self.l_vib.set_data(self._t[:n], self._vib[:n])
        self.l_aco.set_data(self._t[:n], self._aco[:n])
        self.l_temp.set_data(np.arange(m), self._temp[:m])
        return self.l_vib, self.l_aco, self.l_temp

    def on_click(self, _event):
        self.sample_once()


if __name__ == "__main__":
    demo = Demo()
    plt.show()
