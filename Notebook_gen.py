#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parametric Notebook Generator
Author: Michael.ma & GPT-5
Description:
  A fully configurable PDF notebook generator supporting Cornell notes,
  Four-line grids, Tianzi grids, and other templates.
Usage:
  python notebook_generator.py config.json
"""

import json
import sys
from reportlab.lib.pagesizes import A0, A1, A2, A3, A4, A5, B0, B1, B2, B3, B4, B5, landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# -----------------------------
# 📏 基础单位与纸张尺寸表
# -----------------------------
PAPER_SIZES = {
    "A0": A0, "A1": A1, "A2": A2, "A3": A3, "A4": A4, "A5": A5,
    "B0": B0, "B1": B1, "B2": B2, "B3": B3, "B4": B4, "B5": B5,
}

def mm_to_pt(mm):  # 1 inch = 25.4 mm, 1 inch = 72 pt
    return mm * 72.0 / 25.4

def g_to_pt(g, grid_unit_mm):
    return g * mm_to_pt(grid_unit_mm)

def get_page_size(name, orientation="portrait"):
    size = PAPER_SIZES.get(name.upper(), A4)
    return landscape(size) if orientation == "landscape" else portrait(size)

# -----------------------------
# 🧩 Grid 渲染器
# -----------------------------
class GridRenderer:
    def __init__(self, c: canvas.Canvas, grid_unit_mm: float):
        self.c = c
        self.grid_unit_mm = grid_unit_mm

    def draw_four_line_three_grid(self, x, y, width, height, rows):
        """绘制四线三格（拼音/英语本样式）"""
        line_height = height / rows
        for i in range(rows + 1):
            ypos = y + i * line_height
            if i % 3 == 0:
                self.c.setStrokeColor(colors.black)
                self.c.setLineWidth(0.6)
            else:
                self.c.setStrokeColor(colors.lightgrey)
                self.c.setLineWidth(0.3)
            self.c.line(x, ypos, x + width, ypos)

    def draw_tianzige(self, x, y, width, height, rows, cols):
        """田字格"""
        cell_w = width / cols
        cell_h = height / rows
        for i in range(rows + 1):
            ypos = y + i * cell_h
            self.c.line(x, ypos, x + width, ypos)
        for j in range(cols + 1):
            xpos = x + j * cell_w
            self.c.line(xpos, y, xpos, y + height)

    def draw_dotgrid(self, x, y, width, height, rows, cols):
        """点阵格"""
        dx = width / cols
        dy = height / rows
        r = 0.4
        for i in range(rows + 1):
            for j in range(cols + 1):
                self.c.circle(x + j * dx, y + i * dy, r, stroke=0, fill=1)

# -----------------------------
# 🧱 Cornell 模板渲染
# -----------------------------
class CornellRenderer:
    def __init__(self, c: canvas.Canvas, config, grid_renderer: GridRenderer):
        self.c = c
        self.cfg = config
        self.grid = grid_renderer

    def render(self, x, y, width, height):
        gpt = lambda n: g_to_pt(n, self.cfg["grid_unit_mm"])
        theme_h = gpt(self.cfg["cornell"]["theme_height_mm"])
        sum_h = gpt(self.cfg["cornell"]["summary_height_mm"])
        key_w = gpt(self.cfg["cornell"]["keyword_width"])

        # 区域划分
        main_h = height - theme_h - sum_h
        # 绘制分区线
        self.c.setStrokeColor(colors.black)
        self.c.rect(x, y, width, height, stroke=1, fill=0)

        # 横线
        self.c.line(x, y + sum_h, x + width, y + sum_h)
        self.c.line(x, y + sum_h + main_h, x + width, y + sum_h + main_h)
        # 竖线
        self.c.line(x + key_w, y + sum_h, x + key_w, y + sum_h + main_h)

        # Label
        self.c.setFont("Helvetica", 8)
        self.c.drawString(x + 3, y + height - theme_h + 2, "主题 / Topic")
        self.c.drawString(x + 3, y + sum_h + main_h - 10, "内容 / Notes")
        self.c.drawString(x + 3, y + 2, "总结 / Summary")

# -----------------------------
# 📄 Notebook 生成器
# -----------------------------
class NotebookGenerator:
    def __init__(self, config):
        self.cfg = config
        self.page_size = get_page_size(config["paper"], config["orientation"])
        self.grid_unit_mm = config.get("grid_unit_mm", 3.0)
        self.filename = config.get("output", f"{config['template']}_{config['paper']}.pdf")
        self.c = canvas.Canvas(self.filename, pagesize=self.page_size)
        self.grid = GridRenderer(self.c, self.grid_unit_mm)

    def draw_header(self, w, h):
        c = self.c
        margin = self.cfg["margins"]
        header_h = mm_to_pt(self.cfg["header_height"])
        c.setFont("Helvetica-Bold", 10)
        c.rect(margin["left"], h - margin["top"] - header_h, w - margin["left"] - margin["right"], header_h, stroke=1)
        c.drawString(margin["left"] + 10, h - margin["top"] - header_h + 4, "日期: ______  天气: ______  名言: ___________________________")

    def draw_footer(self, w):
        c = self.c
        margin = self.cfg["margins"]
        footer_h = mm_to_pt(self.cfg["footer_height"])
        c.setFont("Helvetica", 8)
        c.rect(margin["left"], margin["bottom"], w - margin["left"] - margin["right"], footer_h, stroke=1)
        c.drawString(margin["left"] + 10, margin["bottom"] + 2, "备注区 / Footer Info")

    def draw_body(self, w, h):
        margin = self.cfg["margins"]
        top_y = h - margin["top"] - mm_to_pt(self.cfg["header_height"])
        bot_y = margin["bottom"] + mm_to_pt(self.cfg["footer_height"])
        usable_h = top_y - bot_y
        usable_w = w - margin["left"] - margin["right"]

        if self.cfg["template"] == "cornell":
            cornell = CornellRenderer(self.c, self.cfg, self.grid)
            cornell.render(margin["left"], bot_y, usable_w, usable_h)

        elif self.cfg["template"] == "fourline":
            rows = int(usable_h / g_to_pt(3, self.grid_unit_mm))
            self.grid.draw_four_line_three_grid(margin["left"], bot_y, usable_w, usable_h, rows)

        elif self.cfg["template"] == "tianzige":
            self.grid.draw_tianzige(margin["left"], bot_y, usable_w, usable_h, 10, 8)

        elif self.cfg["template"] == "dotgrid":
            self.grid.draw_dotgrid(margin["left"], bot_y, usable_w, usable_h, 40, 30)

        elif self.cfg["template"] == "lined":
            rows = int(usable_h / g_to_pt(3, self.grid_unit_mm))
            for i in range(rows):
                y = bot_y + i * g_to_pt(3, self.grid_unit_mm)
                self.c.line(margin["left"], y, margin["left"] + usable_w, y)

    def generate(self):
        w, h = self.page_size
        self.draw_header(w, h)
        self.draw_footer(w)
        self.draw_body(w, h)
        self.c.showPage()
        self.c.save()
        print(f"✅ PDF 已生成: {self.filename}")

# -----------------------------
# 🚀 主函数入口
# -----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python notebook_generator.py config.json")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        config = json.load(f)

    ng = NotebookGenerator(config)
    ng.generate()

if __name__ == "__main__":
    main()
