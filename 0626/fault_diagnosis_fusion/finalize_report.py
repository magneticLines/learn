# -*- coding: utf-8 -*-
"""报告收尾（需 Windows + Word）：更新目录域、设封面无页眉/页脚、导出 PDF。

build_report.py 生成的 docx 中目录为 TOC 域、首页页眉沿用正文页眉；
本脚本用 Word COM 完成只能由 Word 可靠处理的收尾：
  1) 更新 TOC 域生成目录与页码；
  2) 首页（封面）启用独立页眉/页脚并清空（封面不显示页眉与页码）；
  3) 导出同名 PDF 便于检查。

运行：python finalize_report.py
"""
import os
import win32com.client as win32

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.abspath(os.path.join(ROOT, "..", "大作业报告_工业故障诊断融合.docx"))
PDF = os.path.abspath(os.path.join(ROOT, "..", "大作业报告_工业故障诊断融合.pdf"))

WD_FIRST_PAGE = 2  # wdHeaderFooterFirstPage
WD_PDF = 17        # wdExportFormatPDF


def main():
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    d = word.Documents.Open(DOCX)
    try:
        for sec in d.Sections:
            sec.PageSetup.DifferentFirstPageHeaderFooter = True
            sec.Headers(WD_FIRST_PAGE).Range.Text = ""
            sec.Footers(WD_FIRST_PAGE).Range.Text = ""
        for toc in d.TablesOfContents:
            toc.Update()
        d.Repaginate()
        for toc in d.TablesOfContents:
            toc.Update()
        d.Save()
        d.ExportAsFixedFormat(PDF, WD_PDF)
        print("已更新目录、设封面无页眉并导出 PDF:", PDF, "页数:", d.ComputeStatistics(2))
    finally:
        d.Close(False)
        word.Quit()


if __name__ == "__main__":
    main()
