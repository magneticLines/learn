# Prompt — Figure & Table Caption Generator

## Task
Generate a professional, self-contained caption for a figure or table based on the user's description.

## Input Variables
- `{{type}}` — `figure` or `table`
- `{{description}}` — plain-language description of what the figure/table shows
- `{{template}}` — target journal template (ieee | acm | nature | chinese)
- `{{number}}` — figure/table number (e.g., 1, 2, A1)
- `{{lang}}` — output language (en | zh), auto-detected if omitted

## Caption Conventions by Template

| Template | Figure label | Table label | Caption position |
|----------|-------------|-------------|-----------------|
| ieee | Fig. X. | TABLE X | Figure: below · Table: above |
| acm | Figure X. | Table X. | Figure: below · Table: above |
| nature | Figure X \| | Table X \| | Figure: below · Table: above |
| chinese | 图X | 表X | 图题在下方，表题在上方 |

## Writing Guidelines

1. **Self-contained** — the caption must be understandable without reading the main text.
2. **Structure** — lead with what is shown, then add key details (axes, conditions, units, sample size).
3. **Length** — figures: 1–3 sentences; tables: 1–2 sentences.
4. **Statistical details** — include error bar definitions (e.g., "Error bars represent ± 1 s.d., n = 3") where applicable.
5. **Abbreviations** — define all abbreviations used in the figure/table, even if defined in the main text.
6. **Chinese captions** — use full-width punctuation; end with句号; include English translation for key terms on first use.

## Examples

**IEEE Figure:**
> Fig. 3. Comparison of training loss curves across five models over 100 epochs on the CIFAR-10 dataset. Solid lines indicate training loss; dashed lines indicate validation loss. All models were trained with identical hyperparameters.

**Nature Figure:**
> Figure 2 | Structural overview of the proposed attention mechanism. **a**, Global self-attention layer applied across all input tokens. **b**, Local window attention with stride 2. **c**, Combined output after residual connection. Scale bars: 10 μm.

**中文期刊图题：**
> 图3 五种模型在CIFAR-10数据集上训练100轮的损失曲线对比。实线表示训练损失，虚线表示验证损失。所有模型采用相同超参数训练。

**IEEE Table:**
> TABLE II
> Performance Comparison of Baseline Methods on Three Benchmark Datasets. Best results are shown in bold. OOM indicates out-of-memory error. All experiments were run on a single NVIDIA A100 GPU.

**中文期刊表题：**
> 表2 三个基准数据集上各基线方法的性能对比（加粗为最优结果）
