"""端到端主流程：生成数据 → 提取特征 → 融合实验 → 出图 → 保存指标。

运行：
    python src/pipeline.py
产物：
    figures/*.png      报告与 PPT 用图
    results/metrics.json  各配置准确率等指标
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from mock_sensors import generate_dataset, CLASSES
from features import build_matrix
from fusion import run_experiments
import visualize as viz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, "figures")
RES_DIR = os.path.join(ROOT, "results")


def main(n_per_class=200, seed=42):
    print("[1/4] 生成多传感器 mock 数据 ...")
    samples, example = generate_dataset(n_per_class=n_per_class, seed=seed)
    print(f"      样本总数 = {len(samples)}（{len(CLASSES)} 类 × {n_per_class}）")

    print("[2/4] 提取时域/频域/温度特征 ...")
    X, y, names, sensors = build_matrix(samples)
    print(f"      特征矩阵 = {X.shape}，特征数 = {len(names)}")

    print("[3/4] 训练单传感器基线与融合模型 ...")
    res = run_experiments(X, y, names, sensors, seed=seed)
    for name, c in res["configs"].items():
        print(f"      {name:>12s}: 准确率 = {c['acc']:.3f}")

    print("[4/4] 生成图表 ...")
    os.makedirs(FIG_DIR, exist_ok=True)
    paths = []
    paths.append(viz.plot_waveforms(example, FIG_DIR))
    paths.append(viz.plot_spectra(example, FIG_DIR))
    paths.append(viz.plot_acoustic_temp(example, FIG_DIR))
    paths.append(viz.plot_accuracy_comparison(res["configs"], FIG_DIR))
    paths.append(viz.plot_confusion_matrices(res["configs"], res["classes"], FIG_DIR))
    paths.append(viz.plot_feature_importance(res["fused_importance"], FIG_DIR))
    for p in paths:
        print("      saved", os.path.relpath(p, ROOT))

    # 保存指标
    os.makedirs(RES_DIR, exist_ok=True)
    metrics = {
        "classes": res["classes"],
        "n_samples": len(samples),
        "n_features": len(names),
        "split": {"train": res["split"][0], "test": res["split"][1]},
        "accuracy": {name: c["acc"] for name, c in res["configs"].items()},
        "top_features": [
            {"name": n, "importance": round(float(v), 4)}
            for n, v in res["fused_importance"][:10]
        ],
        "confusion_matrices": {
            name: c["cm"].tolist() for name, c in res["configs"].items()
        },
    }
    mp = os.path.join(RES_DIR, "metrics.json")
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print("      saved", os.path.relpath(mp, ROOT))

    # 文本报告
    rp = os.path.join(RES_DIR, "classification_reports.txt")
    with open(rp, "w", encoding="utf-8") as f:
        for name, c in res["configs"].items():
            f.write(f"==== {name}  (准确率 {c['acc']:.3f}) ====\n{c['report']}\n\n")
    print("      saved", os.path.relpath(rp, ROOT))

    fused = res["configs"]["三传感器融合"]["acc"]
    best_single = max(res["configs"][k]["acc"] for k in ["仅振动", "仅声学", "仅温度"])
    print(f"\n结论：融合准确率 {fused:.1%}，较最佳单传感器 {best_single:.1%} "
          f"提升 {(fused - best_single) * 100:.1f} 个百分点。")
    return metrics


if __name__ == "__main__":
    main()
