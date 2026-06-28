"""特征提取：从三类传感器信号中提取时域 / 频域 / 温度特征。

每个特征都标注其所属传感器，便于做"单传感器 vs 融合"的对比实验。
"""
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.stats import kurtosis, skew

from mock_sensors import FS, BPFO, BPFI, BSF, _SQUEAL_FREQ


def _band_energy(freqs, mag, center, half_width=15.0):
    """指定中心频率附近频带的能量占比。"""
    mask = (freqs >= center - half_width) & (freqs <= center + half_width)
    total = np.sum(mag) + 1e-12
    return float(np.sum(mag[mask]) / total)


def vib_time_features(sig):
    """振动时域特征。"""
    rms = float(np.sqrt(np.mean(sig ** 2)))
    peak = float(np.max(np.abs(sig)))
    return {
        "vib_rms": rms,
        "vib_peak": peak,
        "vib_kurtosis": float(kurtosis(sig)),       # 峭度：冲击越强越大
        "vib_crest": float(peak / (rms + 1e-12)),   # 峰值因子
        "vib_std": float(np.std(sig)),
    }


def vib_freq_features(sig, fs=FS):
    """振动频域特征：各故障特征频率处的频带能量 + 频谱重心。"""
    mag = np.abs(rfft(sig))
    freqs = rfftfreq(len(sig), 1 / fs)
    centroid = float(np.sum(freqs * mag) / (np.sum(mag) + 1e-12))
    return {
        "vib_e_bpfo": _band_energy(freqs, mag, BPFO),
        "vib_e_bpfi": _band_energy(freqs, mag, BPFI),
        "vib_e_bsf": _band_energy(freqs, mag, BSF),
        "vib_centroid": centroid,
    }


def acoustic_features(sig, fs=FS):
    """声学特征：宽带能量、频谱熵、高频能量占比、异响频带能量。"""
    mag = np.abs(rfft(sig))
    freqs = rfftfreq(len(sig), 1 / fs)
    p = mag / (np.sum(mag) + 1e-12)
    entropy = float(-np.sum(p * np.log(p + 1e-12)))      # 频谱熵：越无序越大
    hf_ratio = float(np.sum(mag[freqs > 2000]) / (np.sum(mag) + 1e-12))
    return {
        "aco_rms": float(np.sqrt(np.mean(sig ** 2))),
        "aco_entropy": entropy,
        "aco_hf_ratio": hf_ratio,
        "aco_e_squeal": _band_energy(freqs, mag, _SQUEAL_FREQ, half_width=120.0),
    }


def temp_features(seq):
    """温度特征：均值、最大值、温升梯度、热点数。"""
    grad = np.gradient(seq)
    mean = float(np.mean(seq))
    hotspot = int(np.sum(grad > (np.mean(grad) + 2 * np.std(grad))))
    return {
        "temp_mean": mean,
        "temp_max": float(np.max(seq)),
        "temp_slope": float(np.max(grad)),       # 最大温升速率
        "temp_rise": float(seq[-1] - seq[0]),    # 总温升
        "temp_hotspot": float(hotspot),
    }


# 每个特征所属的传感器（用于单传感器实验分组）
def sensor_of(feature_name):
    return feature_name.split("_")[0]   # vib / aco / temp


def extract_all(sample):
    """对一个样本提取全部特征，返回有序 dict。"""
    feats = {}
    feats.update(vib_time_features(sample["vib"]))
    feats.update(vib_freq_features(sample["vib"]))
    feats.update(acoustic_features(sample["aco"]))
    feats.update(temp_features(sample["temp"]))
    return feats


def build_matrix(samples):
    """把样本列表转成特征矩阵。

    返回:
      X: (n_samples, n_features) ndarray
      y: (n_samples,) ndarray
      feature_names: list[str]
      sensors: list[str]，与 feature_names 对应的传感器归属
    """
    rows, y = [], []
    feature_names = None
    for s in samples:
        f = extract_all(s)
        if feature_names is None:
            feature_names = list(f.keys())
        rows.append([f[k] for k in feature_names])
        y.append(s["label"])
    X = np.array(rows, dtype=float)
    sensors = [sensor_of(n) for n in feature_names]
    return X, np.array(y), feature_names, sensors


if __name__ == "__main__":
    from mock_sensors import generate_dataset, CLASSES
    samples, _ = generate_dataset(n_per_class=20)
    X, y, names, sensors = build_matrix(samples)
    print(f"特征矩阵 X={X.shape}，标签 y={y.shape}")
    print(f"特征数={len(names)}，传感器分布={ {s: sensors.count(s) for s in set(sensors)} }")
    print("特征名:", names)
