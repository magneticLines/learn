# -*- coding: utf-8 -*-
"""生成课程大作业报告 docx（题目 8：工业设备故障诊断多传感器融合）。

按范文章节结构生成：封面 → 摘要/关键词 → 目录 → 第1~6章 → 参考文献，
正文宋体小四、1.5 倍行距，标题黑体加粗，嵌入 figures/ 下 6 张图与结果表。

运行：python build_report.py
输出：../大作业报告_工业故障诊断融合.docx
"""
import os
import json

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figures")
OUT = os.path.abspath(os.path.join(ROOT, "..", "大作业报告_工业故障诊断融合.docx"))
METRICS = json.load(open(os.path.join(ROOT, "results", "metrics.json"), encoding="utf-8"))

CN = "宋体"
CN_HEI = "黑体"
EN = "Times New Roman"


def set_cn_font(run, cn=CN, en=EN, size=None, bold=None, color=None):
    run.font.name = en
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), en)
    rfonts.set(qn("w:hAnsi"), en)
    rfonts.set(qn("w:eastAsia"), cn)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.size = Pt(12)            # 小四
    normal.font.name = EN
    normal._element.get_or_add_rPr().append(OxmlElement("w:rFonts"))
    set_cn_font_style(normal, CN, EN, 12)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(0)


def set_cn_font_style(style, cn, en, size):
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), en)
    rfonts.set(qn("w:hAnsi"), en)
    rfonts.set(qn("w:eastAsia"), cn)


def heading(doc, text, level):
    sizes = {1: 16, 2: 14, 3: 12}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    # 用 outline level 以便目录识别
    ppr = p._p.get_or_add_pPr()
    outline = OxmlElement("w:outlineLvl")
    outline.set(qn("w:val"), str(level - 1))
    ppr.append(outline)
    run = p.add_run(text)
    set_cn_font(run, cn=CN_HEI, size=sizes.get(level, 12), bold=True)
    return p


def body(doc, text, indent=True, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)   # 首行缩进 2 字符
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    set_cn_font(run, size=12)
    return p


def add_figure(doc, path, caption, width_in=5.8):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    run = p.add_run()
    run.add_picture(path, width=Inches(width_in))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    crun = cap.add_run(caption)
    set_cn_font(crun, size=10.5, bold=True)


def add_toc(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_sep = OxmlElement("w:fldChar"); fld_sep.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "（右键“更新域”生成目录）"
    fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
    for e in (fld_begin, instr, fld_sep, t, fld_end):
        run._r.append(e)


def title_line(doc, text, size, bold=True, space_after=6, cn=CN_HEI):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run = p.add_run(text)
    set_cn_font(run, cn=cn, size=size, bold=bold)
    return p


def build():
    doc = Document()
    setup_styles(doc)
    sec = doc.sections[0]
    sec.top_margin = Inches(1); sec.bottom_margin = Inches(1)
    sec.left_margin = Inches(1.1); sec.right_margin = Inches(1)

    acc = METRICS["accuracy"]
    fused = acc["三传感器融合"]
    best_single = max(acc["仅振动"], acc["仅声学"], acc["仅温度"])

    # ---------------- 封面 ----------------
    for _ in range(3):
        doc.add_paragraph()
    title_line(doc, "《多传感器数据融合》课程大作业", 18)
    title_line(doc, "工业设备故障诊断多传感器融合设计与实现", 16, space_after=4)
    title_line(doc, "——基于振动 + 声学 + 红外温度的滚动轴承故障诊断", 12, bold=False, cn=CN)
    for _ in range(6):
        doc.add_paragraph()
    for label in ["学生姓名：________________", "学    号：________________",
                  "班    级：________________", "指导教师：________________",
                  "完成日期：2026 年 6 月"]:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        set_cn_font(p.add_run(label), size=12)
    doc.add_page_break()

    # ---------------- 摘要 ----------------
    title_line(doc, "摘  要", 14)
    body(doc,
         "针对工业旋转设备（滚动轴承）故障诊断中单一传感器信息不完整、易受工况与噪声干扰、"
         "诊断鲁棒性不足的问题，本文设计并实现了一套基于振动、声学与红外温度三类传感器的"
         "多传感器特征级融合故障诊断方法。由于实验条件限制，本文按故障机理对三类传感器信号"
         "进行模拟生成，覆盖正常、内圈故障、外圈故障、滚动体故障四种典型工况。系统分别从"
         "振动信号提取时域（均方根、峭度、峰值因子）与频域（轴承故障特征频率 BPFI/BPFO/BSF "
         "频带能量）特征，从声学信号提取频谱熵、高频能量占比与异响频带能量特征，从红外温度"
         "提取均值、温升梯度、热点数等特征，共 18 维。采用特征级融合策略将三类传感器特征拼接，"
         "并以随机森林作为分类器实现故障诊断。实验结果表明：仅振动、仅声学、仅温度的诊断准确率"
         f"分别为 {acc['仅振动']:.1%}、{acc['仅声学']:.1%}、{acc['仅温度']:.1%}，"
         f"而三传感器融合准确率达 {fused:.1%}，较最佳单传感器提升约 "
         f"{(fused - best_single) * 100:.1f} 个百分点，验证了多传感器融合在提升故障诊断"
         "准确率与鲁棒性方面的有效性。")
    p = doc.add_paragraph(); p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    set_cn_font(p.add_run("关键词："), cn=CN_HEI, size=12, bold=True)
    set_cn_font(p.add_run("多传感器融合；故障诊断；滚动轴承；特征级融合；随机森林"), size=12)
    doc.add_page_break()

    # ---------------- 目录 ----------------
    title_line(doc, "目  录", 14)
    add_toc(doc)
    doc.add_page_break()

    # ---------------- 第1章 ----------------
    heading(doc, "第1章 绪论", 1)
    heading(doc, "1.1 研究背景与意义", 2)
    body(doc, "工业旋转设备广泛应用于电力、冶金、石化、制造等领域，滚动轴承作为其核心部件，"
              "长期运行在高速、重载、变工况环境下，是设备故障的高发部位。轴承故障若不能及时发现，"
              "轻则导致停机停产，重则引发安全事故。因此，对设备进行状态监测与故障诊断具有重要的"
              "工程价值与经济意义。")
    body(doc, "传统故障诊断多依赖单一振动传感器。然而单一传感器获取的信息维度有限：振动信号"
              "对故障类型敏感但易受机械噪声干扰；声学信号便于非接触监测却难以分辨故障类型；"
              "温度信号反映设备整体热状态却存在滞后。单一信息源难以在复杂工况下保证诊断的准确性"
              "与鲁棒性。多传感器融合通过整合互补信息，有望突破单一传感器的局限。")
    heading(doc, "1.2 国内外研究现状", 2)
    body(doc, "在故障诊断领域，基于振动信号的时频分析、包络解调、经验模态分解等方法已较为成熟；"
              "近年来以支持向量机、随机森林、深度神经网络为代表的智能诊断方法显著提升了诊断精度。"
              "在多传感器融合方面，按融合层次可分为数据级、特征级与决策级融合：数据级保留信息最全"
              "但对配准要求高；决策级实现简单但损失细节；特征级融合在信息保留与实现复杂度之间取得"
              "较好平衡，成为工程中的常用方案。")
    body(doc, "总体来看，已有研究多聚焦单一信号或两类信号融合，针对振动—声学—温度三类异构传感器"
              "在统一框架下的特征级融合诊断仍有进一步工程实践与对比验证的空间。")
    heading(doc, "1.3 本文主要工作", 2)
    body(doc, "本文主要工作包括：①按故障机理模拟生成振动、声学、红外温度三类传感器在四种工况下"
              "的信号数据；②分别设计三类传感器的时域、频域与统计特征提取方法；③构建特征级融合"
              "框架并以随机森林实现故障分类；④通过单传感器与融合的对比实验，量化评估多传感器融合"
              "的有效性；⑤实现可交互的实时诊断演示系统。")

    # ---------------- 第2章 ----------------
    heading(doc, "第2章 相关理论基础", 1)
    heading(doc, "2.1 多传感器融合层次", 2)
    body(doc, "多传感器融合是指综合利用多个传感器在时间或空间上的冗余与互补信息，以获得比单一"
              "传感器更准确、更可靠的状态估计。按融合发生的层次可分为：数据级融合（直接融合原始"
              "信号）、特征级融合（融合各传感器提取的特征向量）与决策级融合（融合各传感器独立判决"
              "结果）。本文采用特征级融合，将三类传感器特征拼接为统一特征向量后送入分类器。")
    heading(doc, "2.2 轴承故障特征频率", 2)
    body(doc, "滚动轴承不同部位发生局部损伤时，会在振动信号中激起以特定频率出现的周期性冲击，"
              "称为故障特征频率，主要包括内圈故障频率 BPFI、外圈故障频率 BPFO 与滚动体故障频率 "
              "BSF。这些特征频率由轴承几何参数与转速决定，是区分故障类型的关键依据，构成本文"
              "振动频域特征的物理基础。")
    heading(doc, "2.3 随机森林分类器", 2)
    body(doc, "随机森林是一种基于决策树的集成学习方法，通过对样本与特征的随机采样训练多棵决策树"
              "并以投票方式输出结果，具有抗过拟合能力强、对特征量纲不敏感、可输出特征重要性等优点，"
              "适合处理本文这类多源异构特征的分类问题。")

    # ---------------- 第3章 ----------------
    heading(doc, "第3章 系统设计与数据生成", 1)
    heading(doc, "3.1 总体框架", 2)
    body(doc, "系统总体流程为：多传感器数据生成 → 各传感器特征提取 → 特征级融合 → 随机森林分类"
              " → 诊断结果与可视化。三类传感器并行采集，特征提取后拼接为统一特征向量，由分类器"
              "输出四种工况之一。")
    heading(doc, "3.2 多传感器数据生成", 2)
    body(doc, "在无真实传感器的条件下，本文按物理机理模拟生成数据。振动信号由转频谐波、故障特征"
              "频率处的周期性冲击与包络谱线、测量噪声叠加而成；声学信号在振动声辐射基础上叠加故障"
              "异响与环境噪声，其异响形态在各故障类型间相近；红外温度按一阶温升模型生成稳态温度并"
              "叠加故障热点。四种工况各生成 200 个样本，共 800 个样本。三类传感器在工况区分能力上"
              "各有侧重且存在重叠，以贴近真实场景并体现融合价值。")
    add_figure(doc, os.path.join(FIG, "fig1_vibration_waveform.png"),
               "图 3-1  四种工况的振动时域波形")
    add_figure(doc, os.path.join(FIG, "fig2_vibration_spectrum.png"),
               "图 3-2  振动频谱与故障特征频率（BPFI/BPFO/BSF）")
    add_figure(doc, os.path.join(FIG, "fig3_acoustic_temperature.png"),
               "图 3-3  各工况声学信号与红外温度曲线")
    heading(doc, "3.3 特征提取", 2)
    body(doc, "振动特征包括时域的均方根、峭度、峰值因子、标准差，以及频域的 BPFI/BPFO/BSF 频带"
              "能量占比与频谱重心；声学特征包括均方根、频谱熵、高频能量占比与异响频带能量；温度"
              "特征包括均值、最大值、最大温升梯度、总温升与热点数。三类特征合计 18 维。")
    heading(doc, "3.4 特征级融合与分类", 2)
    body(doc, "将振动、声学、温度三类特征向量按维度拼接，形成 18 维融合特征，送入随机森林"
              "（200 棵决策树）进行四分类。为对比融合效果，另以各单类传感器特征子集分别训练"
              "同结构分类器作为基线。")

    # ---------------- 第4章 ----------------
    heading(doc, "第4章 实验与结果分析", 1)
    heading(doc, "4.1 实验设置", 2)
    body(doc, f"数据集共 {METRICS['n_samples']} 个样本（4 类 × 200），按 7:3 划分为训练集"
              f"（{METRICS['split']['train']} 个）与测试集（{METRICS['split']['test']} 个），"
              "采用分层抽样保证类别均衡。评价指标为故障识别准确率，并辅以混淆矩阵分析各类别表现。")
    heading(doc, "4.2 单传感器与融合准确率对比", 2)
    body(doc, "四种配置在测试集上的准确率如表 4-1 与图 4-1 所示。可以看到，振动单传感器准确率"
              f"最高（{acc['仅振动']:.1%}），因其能较好区分故障类型；声学与温度单传感器准确率"
              f"较低（{acc['仅声学']:.1%}、{acc['仅温度']:.1%}），主要因其分别只能判断“有无故障”"
              "与“严重程度”，难以分辨具体类型。三传感器融合充分利用互补信息，准确率达 "
              f"{fused:.1%}，优于任一单传感器。")
    # 结果表
    add_result_table(doc, acc)
    add_figure(doc, os.path.join(FIG, "fig4_accuracy_comparison.png"),
               "图 4-1  单传感器与多传感器融合准确率对比", width_in=4.6)
    heading(doc, "4.3 混淆矩阵分析", 2)
    body(doc, "图 4-2 给出四种配置的混淆矩阵。单传感器配置在若干类别间存在明显混淆：仅声学、"
              "仅温度配置将三种故障类型大量混淆；仅振动配置主要在正常与轻微故障间存在误判。"
              "融合后各类别的对角线占比显著提高，误判明显减少。")
    add_figure(doc, os.path.join(FIG, "fig5_confusion_matrices.png"),
               "图 4-2  各配置混淆矩阵", width_in=5.2)
    heading(doc, "4.4 特征重要性分析", 2)
    body(doc, "图 4-3 给出融合模型的特征重要性排序。振动频域的故障特征频带能量、声学异响频带"
              "能量与温度相关特征均位居前列，表明三类传感器特征对最终诊断均有实质贡献，从特征"
              "层面印证了多传感器融合的合理性。")
    add_figure(doc, os.path.join(FIG, "fig6_feature_importance.png"),
               "图 4-3  融合模型 Top-10 特征重要性", width_in=4.8)

    # ---------------- 第5章 ----------------
    heading(doc, "第5章 系统实现", 1)
    heading(doc, "5.1 软件模块", 2)
    body(doc, "系统采用 Python 实现，按职责划分为：数据生成模块（mock_sensors）、特征提取模块"
              "（features）、融合与对比实验模块（fusion）、可视化模块（visualize）与端到端主流程"
              "（pipeline）。各模块职责单一、接口清晰，便于维护与扩展。")
    heading(doc, "5.2 实时诊断演示", 2)
    body(doc, "为便于演示，系统实现了交互式诊断界面（demo）：点击按钮即可随机抽取一个工况样本，"
              "动画绘制振动、声学、温度三路信号，并实时给出融合模型的诊断结果，正确与否以颜色区分，"
              "可用于录制演示视频。")
    heading(doc, "5.3 功能测试", 2)
    body(doc, "对数据生成、特征提取、模型训练与诊断流程进行了端到端测试，主流程可一键运行并稳定"
              "产出全部图表与量化指标；交互演示可正常抽样与诊断，系统功能完整可用。")

    # ---------------- 第6章 ----------------
    heading(doc, "第6章 总结与展望", 1)
    heading(doc, "6.1 工作总结", 2)
    body(doc, "本文面向工业设备故障诊断，设计并实现了振动—声学—红外温度三传感器特征级融合诊断"
              "系统，完成了数据模拟、特征提取、融合分类与对比实验全流程。实验表明融合诊断准确率"
              f"达 {fused:.1%}，较最佳单传感器提升约 {(fused - best_single) * 100:.1f} 个百分点。")
    heading(doc, "6.2 主要创新点", 2)
    body(doc, "①构建了振动、声学、红外温度三类异构传感器统一的特征级融合诊断框架；"
              "②设计了体现三类传感器“类型—有无—严重度”互补性的特征体系；"
              "③通过系统的单传感器与融合对比实验，从准确率、混淆矩阵与特征重要性三个角度"
              "量化验证了融合的有效性。")
    heading(doc, "6.3 不足与展望", 2)
    body(doc, "本文数据为机理模拟生成，与真实工况仍有差距；融合方式为特征级拼接，未充分建模"
              "传感器间的时序关联。后续可引入公开数据集（如 CWRU）验证，并探索决策级融合、"
              "注意力加权融合及深度学习方法，以进一步提升复杂工况下的诊断性能。")

    # ---------------- 参考文献 ----------------
    heading(doc, "参考文献", 1)
    refs = [
        "[1] 雷亚国, 贾峰, 孔德同, 等. 大数据下机械智能故障诊断的机遇与挑战[J]. 机械工程学报, 2018, 54(5): 94-104.",
        "[2] Randall R B, Antoni J. Rolling element bearing diagnostics—A tutorial[J]. Mechanical Systems and Signal Processing, 2011, 25(2): 485-520.",
        "[3] Breiman L. Random forests[J]. Machine Learning, 2001, 45(1): 5-32.",
        "[4] 韩崇昭, 朱洪艳, 段战胜. 多源信息融合[M]. 北京: 清华大学出版社, 2010.",
        "[5] Smith W A, Randall R B. Rolling element bearing diagnostics using the Case Western Reserve University data: A benchmark study[J]. Mechanical Systems and Signal Processing, 2015, 64-65: 100-131.",
        "[6] 张西宁, 雷威, 余迪. 多传感器信息融合在旋转机械故障诊断中的应用综述[J]. 振动与冲击, 2020, 39(20): 1-12.",
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.left_indent = Pt(0)
        set_cn_font(p.add_run(r), size=10.5)

    doc.save(OUT)
    print("报告已生成:", OUT)


def add_result_table(doc, acc):
    cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cn_font(cap.add_run("表 4-1  各配置故障识别准确率"), size=10.5, bold=True)
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for c, txt in zip(hdr, ["配置", "故障识别准确率"]):
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cn_font(c.paragraphs[0].add_run(txt), cn=CN_HEI, size=11, bold=True)
    order = ["仅振动", "仅声学", "仅温度", "三传感器融合"]
    for name in order:
        cells = table.add_row().cells
        set_cn_font(cells[0].paragraphs[0].add_run(name), size=11,
                    bold=(name == "三传感器融合"))
        cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cn_font(cells[1].paragraphs[0].add_run(f"{acc[name]:.1%}"), size=11,
                    bold=(name == "三传感器融合"))
    doc.add_paragraph()


if __name__ == "__main__":
    build()
