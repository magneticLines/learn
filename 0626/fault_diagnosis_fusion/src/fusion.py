"""多传感器融合与对比实验。

实验设计：分别用「单一传感器特征」和「三传感器特征级融合」训练随机森林分类器，
对比故障识别准确率，验证多传感器融合的价值。

融合策略：特征级融合（feature-level fusion）——将三类传感器特征拼接成统一特征向量。
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


def _subset(X, sensors, keep):
    """按传感器归属选取特征列。keep 为传感器名集合，如 {'vib'} 或 {'vib','aco','temp'}。"""
    idx = [i for i, s in enumerate(sensors) if s in keep]
    return X[:, idx], idx


def run_experiments(X, y, feature_names, sensors, seed=42):
    """运行单传感器与融合对比实验。

    返回 results dict：
      {
        'configs': {名称: {'acc':float, 'cm':ndarray, 'report':str}},
        'classes': [...],
        'fused_importance': [(feature_name, importance), ...] 降序,
        'split': (n_train, n_test),
      }
    """
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=seed, stratify=y
    )

    experiments = {
        "仅振动": {"vib"},
        "仅声学": {"aco"},
        "仅温度": {"temp"},
        "三传感器融合": {"vib", "aco", "temp"},
    }

    configs = {}
    fused_importance = None
    for name, keep in experiments.items():
        Xtr_s, idx = _subset(X_tr, sensors, keep)
        Xte_s, _ = _subset(X_te, sensors, keep)
        clf = RandomForestClassifier(
            n_estimators=200, max_depth=None, random_state=seed, n_jobs=-1
        )
        clf.fit(Xtr_s, y_tr)
        pred = clf.predict(Xte_s)
        acc = accuracy_score(y_te, pred)
        cm = confusion_matrix(y_te, pred)
        from mock_sensors import CLASSES
        report = classification_report(
            y_te, pred, target_names=CLASSES, digits=3, zero_division=0
        )
        configs[name] = {"acc": float(acc), "cm": cm, "report": report}
        if keep == {"vib", "aco", "temp"}:
            imp = clf.feature_importances_
            sub_names = [feature_names[i] for i in idx]
            fused_importance = sorted(
                zip(sub_names, imp), key=lambda x: x[1], reverse=True
            )

    from mock_sensors import CLASSES
    return {
        "configs": configs,
        "classes": CLASSES,
        "fused_importance": fused_importance,
        "split": (len(y_tr), len(y_te)),
    }


if __name__ == "__main__":
    from mock_sensors import generate_dataset
    from features import build_matrix
    samples, _ = generate_dataset(n_per_class=200)
    X, y, names, sensors = build_matrix(samples)
    res = run_experiments(X, y, names, sensors)
    print(f"训练/测试样本数: {res['split']}")
    for name, c in res["configs"].items():
        print(f"  {name:>12s}: 准确率 = {c['acc']:.3f}")
    print("\n融合模型 Top-5 重要特征:")
    for n, imp in res["fused_importance"][:5]:
        print(f"  {n:>14s}: {imp:.3f}")
