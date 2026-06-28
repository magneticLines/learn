"""多传感器数据模拟（无真实传感器，按物理机理生成 mock 数据）。

模拟工业旋转设备（滚动轴承）在四种工况下的三类传感器信号：
  - 振动传感器：加速度时序，含转频谐波 + 故障特征频率冲击 + 噪声
  - 声学麦克风：与振动相关的声压时序，含宽带噪声 + 故障异响
  - 红外温度：设备表面温度时序，含温升曲线 + 故障热点

四种工况（标签）：
  0 正常 / 1 内圈故障 / 2 外圈故障 / 3 滚动体故障

设计上让各工况特征"部分重叠"（每类参数带随机扰动），
单一传感器难以完全区分，从而体现多传感器融合的价值。
"""
import numpy as np

# ---- 采集参数 ----
FS = 12000           # 振动/声学采样率 (Hz)，参考 CWRU 轴承数据集
N = 2048             # 每个样本的振动/声学采样点数
TEMP_LEN = 60        # 温度序列长度（采样 60 次，约 1 分钟）
FR = 30.0            # 转频 (Hz)

# 轴承故障特征频率（近似 CWRU 6205 轴承），单位 Hz
BPFO = 3.585 * FR    # 外圈
BPFI = 5.415 * FR    # 内圈
BSF = 2.357 * FR     # 滚动体

CLASSES = ["正常", "内圈故障", "外圈故障", "滚动体故障"]

# 每类的故障特征频率与强度配置。
# 设计原则（让单一传感器都"看不全"，从而体现融合价值）：
#   - 振动：靠故障特征频率(BPFI/BPFO/BSF)区分"故障类型"，但冲击幅值相近、噪声大，
#           对"正常 vs 轻微故障"区分力有限；
#   - 声学：只反映"有无异响"（三种故障异响形态相近），能判"是否故障"但难判类型；
#   - 温度：三种故障的稳态温度接近且噪声大，主要区分"正常 vs 故障"和大致严重度。
_FAULT_CFG = {
    0: dict(fault_freq=None, impulse_amp=0.0, temp_steady=45.0, temp_slope=0.6, hotspot=0.0),
    1: dict(fault_freq=BPFI, impulse_amp=1.15, temp_steady=51.0, temp_slope=0.95, hotspot=1.0),
    2: dict(fault_freq=BPFO, impulse_amp=1.10, temp_steady=50.0, temp_slope=0.88, hotspot=0.9),
    3: dict(fault_freq=BSF, impulse_amp=1.05, temp_steady=49.0, temp_slope=0.80, hotspot=0.8),
}

# 故障异响的固定频带（三种故障共用，故声学只能判"有无故障"而非类型）
_SQUEAL_FREQ = 2400.0


def _rotation_harmonics(t, rng):
    """转频基波及其谐波（设备正常运转的固有振动）。"""
    sig = np.zeros_like(t)
    for k, amp in zip((1, 2, 3), (1.0, 0.5, 0.25)):
        phase = rng.uniform(0, 2 * np.pi)
        sig += amp * np.sin(2 * np.pi * FR * k * t + phase)
    return sig


def _fault_impulses(t, fault_freq, amp, rng):
    """故障冲击序列：以故障特征频率周期性出现，每次冲击是一段衰减的高频共振。"""
    if fault_freq is None or amp <= 0:
        return np.zeros_like(t)
    sig = np.zeros_like(t)
    period = 1.0 / fault_freq
    carrier = rng.uniform(2800, 3600)     # 结构共振频率
    decay = rng.uniform(600, 900)         # 冲击衰减系数
    n_imp = int(t[-1] / period) + 1
    for i in range(n_imp):
        t0 = i * period + rng.normal(0, period * 0.02)   # 轻微抖动
        local = t - t0
        mask = local >= 0
        env = np.where(mask, np.exp(-decay * np.clip(local, 0, None)), 0.0)
        sig += amp * env * np.sin(2 * np.pi * carrier * local)
    return sig


def generate_vibration(cls, rng):
    t = np.arange(N) / FS
    cfg = _FAULT_CFG[cls]
    amp = cfg["impulse_amp"] * rng.uniform(0.8, 1.2)
    sig = _rotation_harmonics(t, rng)
    sig += _fault_impulses(t, cfg["fault_freq"], amp, rng)
    if cfg["fault_freq"] is not None:
        # 故障特征频率处的包络谱线：让振动频域能区分"故障类型"（内/外/滚动体）。
        # 幅值很小且随机，与噪声底重叠 → 弱故障样本可能被误判为正常（制造可控难度）。
        line_amp = 0.22 * rng.uniform(0.5, 1.5)
        sig += line_amp * np.sin(2 * np.pi * cfg["fault_freq"] * t + rng.uniform(0, 2 * np.pi))
    sig += rng.normal(0, 0.5, N)          # 测量噪声：保留类型可分性，但使正常↔故障存在混淆
    return sig


def generate_acoustic(cls, vib, rng):
    """声学信号：与振动相关（机械声辐射），但叠加独立宽带噪声与故障异响。"""
    cfg = _FAULT_CFG[cls]
    # 声辐射近似为振动的带通响应：用一阶差分突出高频 + 缩放
    aco = np.diff(vib, prepend=vib[0]) * 0.6
    if cfg["fault_freq"] is not None:
        t = np.arange(N) / FS
        # 故障异响：所有故障类型共用同一异响频带，故声学只能判"有无故障"而非类型
        squeal = 0.5 * np.sin(2 * np.pi * _SQUEAL_FREQ * t + rng.uniform(0, 2 * np.pi))
        # 叠加宽带突发噪声（异常异响），同样不区分类型
        burst = rng.normal(0, 0.4, N) * (rng.random(N) < 0.05)
        aco += (squeal + burst) * rng.uniform(0.85, 1.15)
    aco += rng.normal(0, 0.6, N)          # 环境噪声（声学噪声更大）
    return aco


def generate_temperature(cls, rng):
    """温度序列：一阶温升到稳态 + 故障热点尖峰。"""
    cfg = _FAULT_CFG[cls]
    ambient = rng.uniform(23, 27)
    steady = cfg["temp_steady"] + rng.normal(0, 2.0)
    tau = rng.uniform(12, 18) / cfg["temp_slope"]   # 时间常数，slope 越大升温越快
    k = np.arange(TEMP_LEN)
    seq = ambient + (steady - ambient) * (1 - np.exp(-k / tau))
    # 故障热点：随机时刻的温度尖峰
    if cfg["hotspot"] > 0:
        n_spike = rng.integers(2, 5)
        for _ in range(n_spike):
            idx = rng.integers(TEMP_LEN // 3, TEMP_LEN)
            seq[idx:] += cfg["hotspot"] * rng.uniform(0.5, 1.5)
    seq += rng.normal(0, 0.3, TEMP_LEN)   # 测量噪声
    return seq


def generate_sample(cls, rng):
    vib = generate_vibration(cls, rng)
    aco = generate_acoustic(cls, vib, rng)
    temp = generate_temperature(cls, rng)
    return {"vib": vib, "aco": aco, "temp": temp, "label": cls}


def generate_dataset(n_per_class=200, seed=42):
    """生成完整数据集。

    返回:
      samples: list[dict]，每个含 vib/aco/temp/label
      example_per_class: dict[int->dict]，每类一个代表样本（用于绘图）
    """
    rng = np.random.default_rng(seed)
    samples = []
    example_per_class = {}
    for cls in range(len(CLASSES)):
        for i in range(n_per_class):
            s = generate_sample(cls, rng)
            samples.append(s)
            if cls not in example_per_class:
                example_per_class[cls] = s
    rng.shuffle(samples)
    return samples, example_per_class


if __name__ == "__main__":
    samples, ex = generate_dataset(n_per_class=10)
    print(f"生成 {len(samples)} 个样本，每个样本含三传感器信号")
    for cls, s in ex.items():
        print(f"  类别 {cls} {CLASSES[cls]}: vib{s['vib'].shape} aco{s['aco'].shape} temp{s['temp'].shape}")
