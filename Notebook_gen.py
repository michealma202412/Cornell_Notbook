import json
import sys
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.colors import black, lightgrey, blue
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register a font that supports Chinese characters
# Try to find a system font that supports Chinese
def register_chinese_font():
    # Common Chinese font paths on different systems
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
        "C:/Windows/Fonts/msyh.ttc",  # Windows Microsoft YaHei
        "C:/Windows/Fonts/simsun.ttc",  # Windows SimSun
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
        "/usr/share/fonts/truetype/arphic/uming.ttc",  # Linux
    ]
    
    font_name = "ChineseFont"
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                return font_name
            except:
                continue
    
    # If no system font found, use default font (may not show Chinese properly)
    return "Helvetica"

# Register the font
CHINESE_FONT = register_chinese_font()

class GridRenderer:
    """Handles rendering of different grid types"""
    
    @staticmethod
    def draw_four_line_three_grid(c, x, y, width, height, line_spacing=6, row_heights=None):
        """
        绘制四线三格图形，常用于音乐符号或语言学习
        
        Args:
            c: ReportLab画布对象
            x: 起始x坐标
            y: 起始y坐标
            width: 图形宽度
            height: 图形高度
            line_spacing: 行间距，默认为6个单位
            row_heights: 自定义行高配置
        """
        if row_heights is None:
            row_heights = [4, 6, 4]
            
        # 计算可以绘制多少组四线三格
        total_row_height = sum(row_heights)
        n = int(height // total_row_height)
        for i in range(n):
            # 计算每组四线三格的基础Y坐标
            base_y = y - i * total_row_height
            # 1线 - 使用浅灰色虚线
            c.setStrokeColor(lightgrey)
            c.setDash(1, 2)  # 设置为虚线模式(实线1单位，空白2单位)
            c.line(x, base_y, x + width, base_y)
            # 2线 - 使用蓝色实线
            c.setDash()  # 恢复为实线模式
            c.setStrokeColor(blue)
            c.line(x, base_y - row_heights[0], x + width, base_y - row_heights[0])
            # 3线 - 使用蓝色实线
            c.line(x, base_y - row_heights[0] - row_heights[1], x + width, base_y - row_heights[0] - row_heights[1])
            # 4线 - 使用浅灰色实线
            c.setStrokeColor(lightgrey)
            c.line(x, base_y - row_heights[0] - row_heights[1] - row_heights[2], 
                   x + width, base_y - row_heights[0] - row_heights[1] - row_heights[2])

    @staticmethod
    def draw_dotted_grid(c, x, y, width, height, dot_spacing=20):
        """
        绘制点阵网格
        
        Args:
            c: ReportLab画布对象
            x: 起始x坐标
            y: 起始y坐标
            width: 网格宽度
            height: 网格高度
            dot_spacing: 点之间的间距
        """
        c.setFillColor(lightgrey)
        radius = 0.5  # 点的半径
        rows = int(height // dot_spacing) + 1
        cols = int(width // dot_spacing) + 1
        for row in range(rows):
            for col in range(cols):
                dot_x = x + col * dot_spacing
                dot_y = y - row * dot_spacing
                c.circle(dot_x, dot_y, radius, stroke=0, fill=1)
        c.setFillColor(black)  # 重置填充颜色

    @staticmethod
    def draw_english_grid(c, x, y, width, height, line_spacing=8):
        """
        绘制英文练习格线（三线格）
        
        Args:
            c: ReportLab画布对象
            x: 起始x坐标
            y: 起始y坐标
            width: 网格宽度
            height: 网格高度
            line_spacing: 行间距
        """
        n = int(height // line_spacing)
        for i in range(n):
            base_y = y - i * line_spacing
            # 第一线（基线）- 黑色实线
            c.setStrokeColor(black)
            c.setDash()
            c.line(x, base_y, x + width, base_y)
            # 第二线（中间线）- 灰色虚线
            c.setStrokeColor(lightgrey)
            c.setDash(2, 2)
            c.line(x, base_y - line_spacing/2, x + width, base_y - line_spacing/2)
            # 第三线（顶线）- 灰色实线
            c.setStrokeColor(lightgrey)
            c.setDash()
            c.line(x, base_y - line_spacing, x + width, base_y - line_spacing)
        # 恢复默认状态
        c.setStrokeColor(black)
        c.setDash()

    @staticmethod
    def draw_tianzige_grid(c, x, y, width, height, cell_size=30):
        """
        绘制田字格（汉字练习格）
        
        Args:
            c: ReportLab画布对象
            x: 起始x坐标
            y: 起始y坐标
            width: 网格宽度
            height: 网格高度
            cell_size: 每个格子的大小
        """
        rows = int(height // cell_size)
        cols = int(width // cell_size)
        for row in range(rows):
            for col in range(cols):
                cell_x = x + col * cell_size
                cell_y = y - row * cell_size
                # 绘制外框
                c.rect(cell_x, cell_y - cell_size, cell_size, cell_size)
                # 绘制十字线
                c.line(cell_x, cell_y - cell_size/2, cell_x + cell_size, cell_y - cell_size/2)
                c.line(cell_x + cell_size/2, cell_y - cell_size, cell_x + cell_size/2, cell_y)

    @staticmethod
    def draw_single_line_grid(c, x, y, width, height, line_step=14):
        """
        绘制单行线
        
        Args:
            c: ReportLab画布对象
            x: 起始x坐标
            y: 起始y坐标
            width: 网格宽度
            height: 网格高度
            line_step: 行间距
        """
        yy = y
        while yy > y - height:
            c.setStrokeColor(lightgrey)
            c.line(x, yy, x + width, yy)
            yy -= line_step


class ComponentRenderer:
    """Handles rendering of different notebook components"""
    
    def __init__(self, canvas, font):
        self.canvas = canvas
        self.font = font
        
    def draw_text_box(self, x, y, width, height, text, config, alignment="left", vertical_alignment="top"):
        """
        绘制带文本的框
        
        Args:
            x: 起始x坐标
            y: 起始y坐标
            width: 框宽度
            height: 框高度
            text: 要绘制的文本
            config: 配置字典
            alignment: 文本水平对齐方式
            vertical_alignment: 文本垂直对齐方式
        """
        # 绘制框
        self.canvas.rect(x, y, width, height, stroke=1, fill=0)
        
        # 获取文本尺寸
        text_width = self.canvas.stringWidth(text, self.font, 12)
        text_height = 12  # 字体大小
        
        # 获取内边距配置
        text_padding = config.get("text_padding", 2)
        vertical_padding = config.get("vertical_padding", 3)
        
        # 根据垂直对齐方式计算Y坐标
        if vertical_alignment == "top":
            text_y = y + height - vertical_padding - text_height
        elif vertical_alignment == "middle":
            text_y = y + (height / 2) - (text_height / 2)
        else:  # bottom
            text_y = y + vertical_padding
        
        # 根据水平对齐方式计算X坐标
        if alignment == "left":
            text_x = x + text_padding
        elif alignment == "center":
            text_x = x + (width / 2) - (text_width / 2)
        else:  # right
            text_x = x + width - text_padding - text_width
        
        # 绘制文本
        self.canvas.drawString(text_x, text_y, text)
        
        return width, height

    def draw_header(self, x, y, width, height, config):
        """
        绘制页面顶部的标题区域，包括字段框
        
        Args:
            x: 起始x坐标
            y: 起始y坐标
            width: 标题区域宽度
            height: 标题区域高度
            config: 配置字典，包含标题区域的各种设置
        """
        # 设置字体以支持中文显示
        self.canvas.setFont(self.font, 12)

        # 获取字段边距，如果未设置则默认为5
        margin = config.get("field_margin", 5)
        # 初始化光标X坐标
        cursor_x = x + margin
        # 获取字段列表
        fields = config.get("fields", [])
        
        # 如果有字段，计算均匀分布的宽度
        if fields:
            # 计算可用于字段的总宽度（减去边距和字段间距）
            field_spacing = config.get("field_spacing", 5)
            total_field_width = width - 2 * margin - (len(fields) - 1) * field_spacing
            # 每个字段的均匀宽度
            uniform_field_width = total_field_width / len(fields)
        
        # 遍历所有字段并绘制
        for field in fields:
            # 获取文本对齐方式和内边距配置
            text_alignment = field.get("text_alignment", "left")
            text_padding = field.get("text_padding", 2)
            vertical_alignment = field.get("vertical_alignment", "top")
            vertical_padding = field.get("vertical_padding", 3)
            
            # 获取文本尺寸
            text = field["label"] + ":"
            text_width = self.canvas.stringWidth(text, self.font, 12)
            text_height = 12  # 字体大小
            
            # 优先使用统一宽度，但如果文本超长则自适应增加宽度
            field_width = max(uniform_field_width, text_width + 2 * text_padding)
            field_height = max(20, text_height + 2 * vertical_padding)  # 优先使用最小高度20，但若文字更高则自适应
            
            # 根据垂直对齐方式计算Y坐标
            box_y = y - field_height + config.get("field_vertical_padding", 6)
            
            # 使用抽象的文本框绘制函数
            field_config = {
                "text_padding": text_padding,
                "vertical_padding": vertical_padding
            }
            self.draw_text_box(cursor_x, box_y, field_width, field_height, text, field_config, 
                         alignment=text_alignment, vertical_alignment=vertical_alignment)
            
            # 移动光标到下一个字段位置
            field_spacing = config.get("field_spacing", 5)
            cursor_x += field_width + field_spacing

    def draw_quote_box(self, x, y, width, height, config):
        """
        绘制页面顶部的箴言区域
        
        Args:
            x: 起始x坐标
            y: 起始y坐标 (箴言框的顶部y坐标)
            width: 箴言区域宽度
            height: 箴言区域高度
            config: 配置字典，包含页眉区域的各种设置
        """
        # 设置字体以支持中文显示
        self.canvas.setFont(self.font, 12)
        
        # 获取箴言框配置
        quote = config.get("quote_box", None)
        if not quote:
            return
        
        # 获取文本位置配置
        quote_label_padding = config.get("quote_label_padding", 5)
        quote_vertical_padding = quote.get("vertical_padding", 3)
        
        # 获取文本尺寸
        quote_text = quote["label"] + ":"
        quote_text_width = self.canvas.stringWidth(quote_text, self.font, 12)
        quote_text_height = 12  # 字体大小
        
        # 优先使用配置的高度，但如果文本太高则自适应增加高度
        quote_box_height = max(quote["height"], quote_text_height + 2 * quote_vertical_padding)
        
        # 使用抽象的文本框绘制函数
        quote_config = {
            "text_padding": quote_label_padding,
            "vertical_padding": quote_vertical_padding
        }
        self.draw_text_box(x, y, width, quote_box_height, quote_text, quote_config, 
                     alignment="left", vertical_alignment="middle")

    def draw_footer(self, x, y, width, height, config):
        """
        绘制页面底部的页脚区域，包括复习记录和备注
        
        Args:
            x: 起始x坐标
            y: 起始y坐标
            width: 页脚区域宽度
            height: 页脚区域高度
            config: 配置字典，包含页脚区域的各种设置
        """
        # 绘制页脚区域外边框
        self.canvas.setStrokeColor(black)
        self.canvas.rect(x, y, width, height, stroke=1, fill=0)

        # 设置字体以支持中文显示
        self.canvas.setFont(self.font, 12)

        # 获取复习框相关配置
        review_boxes = config.get("review_boxes", [])
        # 初始化光标X坐标(从左侧开始)
        cursor_x = x + config.get("review_label_left_margin", 5)

        # 移动光标到第一个复习框位置
        cursor_x += config.get("review_text_right_spacing", 40)

        # Calculate uniform spacing if there are multiple boxes
        remaining_space = width - (cursor_x - x)
        if len(review_boxes) > 0:
            box_config_width = config.get("review_box_width", 15)
            # Handle "auto" value properly
            if box_config_width == "auto":
                total_config_width = 0  # When auto, we don't pre-allocate space
            else:
                total_config_width = box_config_width * len(review_boxes)
                remaining_space -= total_config_width
            if len(review_boxes) > 1:
                uniform_spacing = remaining_space / (len(review_boxes) - 1)
            else:
                uniform_spacing = config.get("review_box_spacing", 10)
        else:
            uniform_spacing = config.get("review_box_spacing", 10)

        # 遍历所有复习框标签并绘制
        for i, label in enumerate(review_boxes):
            # 获取配置参数
            box_w = config.get("review_box_width", 15)
            box_height = config.get("review_box_height", 5)
            box_top_margin = config.get("review_box_top_margin", 10)
            text_padding = config.get("review_box_text_padding", 2)
            
            # 计算文本尺寸
            text_width = self.canvas.stringWidth(label, self.font, 12)
            text_height = 12  # 字体大小
            
            # 优先使用配置的固定尺寸，但如果文本超长则自适应增加宽度和高度
            # Handle "auto" value properly
            if box_w == "auto":
                box_w = max(15, text_width + 2 * text_padding)  # Use minimum width of 15 or text width
            else:
                box_w = max(box_w, text_width + 2 * text_padding)
            box_height = max(box_height, text_height + 2 * text_padding)  # 保证文本能完整显示
                
            # 绘制复习框
            box_y = y + box_top_margin
            # 使用抽象的文本框绘制函数
            box_config = {
                "text_padding": text_padding,
                "vertical_padding": text_padding
            }
            text_alignment = config.get("review_text_alignment", "center")
            self.draw_text_box(cursor_x, box_y, box_w, box_height, label, box_config, 
                         alignment=text_alignment, vertical_alignment="middle")
            
            # 移动光标到下一个复习框位置
            spacing = uniform_spacing if len(review_boxes) > 1 else config.get("review_box_spacing", 10)
            cursor_x += box_w + spacing

    def draw_cornell_module(self, x, y, width, height, config):
        """
        绘制康奈尔笔记模块，包括主题区、关键词区、笔记区和总结区
        
        Args:
            x: 起始x坐标
            y: 起始y坐标
            width: 模块宽度
            height: 模块高度
            config: 配置字典，包含模块的各种设置
        """
        # 设置字体以支持中文显示
        self.canvas.setFont(self.font, 12)
        
        # 获取各种区域的高度和宽度设置
        theme_h = config.get("theme_height", 14)      # 主题区域高度
        summary_h = config.get("summary_height", 14) # 总结区域高度
        # 修改为按百分比划分宽度，默认3:7
        keyword_width_ratio = config.get("keyword_width_ratio", 0.3)
        keyword_w = width * keyword_width_ratio       # 关键词区域宽度
        line_style = config.get("line_style", "single_line") # 线条样式

        # 绘制康奈尔笔记模块外边框
        self.canvas.setStrokeColor(black)
        self.canvas.rect(x, y - height, width, height, stroke=1, fill=0)

        # 绘制内部区域分割线
        # 主题区域下边界线
        self.canvas.line(x, y - theme_h, x + width, y - theme_h)
        # 总结区域上边界线
        self.canvas.line(x, y - height + summary_h, x + width, y - height + summary_h)
        # 关键词区域右边界线
        self.canvas.line(x + keyword_w, y - theme_h, x + keyword_w, y - height + summary_h)
        
        # 在总结区域内添加水平线，将其分为两行
        summary_mid_y = y - height + summary_h/2
        self.canvas.line(x, summary_mid_y, x + width, summary_mid_y)

        # 根据配置绘制不同的线条样式
        grid_renderer = GridRenderer()
        
        if line_style == "four_line_three_grid":
            # 绘制四线三格图形
            offset_x = keyword_w + config.get("grid_offset_x", 2)
            offset_y = theme_h + config.get("grid_offset_y", 4)
            width_reduction = keyword_w + config.get("grid_width_reduction", 4)
            height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
            # 使用可配置的行间距，默认为6
            line_spacing = config.get("grid_line_spacing", 6)
            # 获取自定义行高配置（上、中、下行高），默认为[4, 6, 4]
            row_heights = config.get("grid_row_heights", [4, 6, 4])
            
            # 在笔记区域绘制四线三格
            grid_renderer.draw_four_line_three_grid(
                self.canvas, x + offset_x, y - offset_y, 
                width - width_reduction, height - height_reduction, 
                line_spacing, row_heights)
            
            # 在关键词区域绘制四线三格
            kw_offset_y = theme_h + config.get("grid_offset_y", 4)
            kw_height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
            grid_renderer.draw_four_line_three_grid(
                self.canvas, x + config.get("grid_offset_x", 2), y - kw_offset_y, 
                keyword_w - config.get("grid_offset_x", 2) * 2, 
                height - kw_height_reduction, line_spacing, row_heights)
            
            # 在总结区域绘制四线三格（修改为铺满整个总结区宽度）
            sum_offset_y = height - summary_h + config.get("grid_offset_y", 4)
            grid_renderer.draw_four_line_three_grid(
                self.canvas, x + config.get("grid_offset_x", 2), y - sum_offset_y, 
                width - config.get("grid_offset_x", 2) * 2, 
                summary_h/2 - config.get("grid_offset_y", 4) * 2, line_spacing, row_heights)
            
            sum_offset_y2 = height - summary_h/2 + config.get("grid_offset_y", 4)
            grid_renderer.draw_four_line_three_grid(
                self.canvas, x + config.get("grid_offset_x", 2), y - sum_offset_y2, 
                width - config.get("grid_offset_x", 2) * 2, 
                summary_h/2 - config.get("grid_offset_y", 4) * 2, line_spacing, row_heights)
            
            # 在主题区域绘制四线三格（新增：铺满整个主题区宽度）
            theme_offset_y = theme_h - config.get("grid_offset_y", 4)
            grid_renderer.draw_four_line_three_grid(
                self.canvas, x + config.get("grid_offset_x", 2), y - theme_offset_y,
                width - config.get("grid_offset_x", 2) * 2,
                theme_h - config.get("grid_offset_y", 4) * 2, line_spacing, row_heights)
                
        elif line_style == "single_line":
            # 绘制单行线
            step = config.get("line_step", 8)           # 行间距
            offset_y = theme_h + config.get("grid_offset_y", 4)     # Y轴偏移量
            bottom_margin = summary_h + config.get("grid_offset_y", 4) # 底部边距
            yy = y - offset_y   # 初始化Y坐标
            
            # 在笔记区域绘制水平线
            while yy > y - height + bottom_margin:
                self.canvas.setStrokeColor(lightgrey)
                self.canvas.line(x + keyword_w + config.get("grid_offset_x", 2), yy, 
                                 x + width - config.get("grid_offset_x", 2), yy)
                yy -= step  # 移动到下一行位置
                
            # 在关键词区域绘制水平线
            kw_y = y - theme_h - config.get("grid_offset_y", 4)
            kw_bottom = y - height + summary_h + config.get("grid_offset_y", 4)
            while kw_y > kw_bottom:
                self.canvas.setStrokeColor(lightgrey)
                self.canvas.line(x + config.get("grid_offset_x", 2), kw_y, 
                                 x + keyword_w - config.get("grid_offset_x", 2), kw_y)
                kw_y -= step
                
            # 在总结区域绘制水平线（修改为铺满整个总结区宽度，并分为两行）
            sum_y = y - height + summary_h - config.get("grid_offset_y", 4)
            mid_summary = y - height + summary_h/2
            while sum_y > mid_summary + config.get("grid_offset_y", 4):
                self.canvas.setStrokeColor(lightgrey)
                self.canvas.line(x + config.get("grid_offset_x", 2), sum_y, 
                                 x + width - config.get("grid_offset_x", 2), sum_y)
                sum_y -= step
                
            sum_y2 = mid_summary - config.get("grid_offset_y", 4)
            while sum_y2 > y - height + config.get("grid_offset_y", 4):
                self.canvas.setStrokeColor(lightgrey)
                self.canvas.line(x + config.get("grid_offset_x", 2), sum_y2, 
                                 x + width - config.get("grid_offset_x", 2), sum_y2)
                sum_y2 -= step
                
            # 在主题区域绘制水平线（新增：铺满整个主题区宽度）
            theme_y = y - theme_h + config.get("grid_offset_y", 4)
            while theme_y < y - config.get("grid_offset_y", 4):
                self.canvas.setStrokeColor(lightgrey)
                self.canvas.line(x + config.get("grid_offset_x", 2), theme_y, 
                                 x + width - config.get("grid_offset_x", 2), theme_y)
                theme_y += step


# ---------------------------
# 主函数：生成笔记本
# ---------------------------
def generate_notebook(config_path):
    """
    根据配置文件生成康奈尔笔记本PDF文件
    
    Args:
        config_path: 配置文件路径(JSON格式)
    """
    # 读取配置文件
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # 获取输出文件名，默认为notebook.pdf
    output = cfg.get("output", "notebook.pdf")
    # 获取页面设置
    page_cfg = cfg.get("page", {})
    # 获取页边距，默认为20
    margin = page_cfg.get("margin", 20)
    # 获取页面方向，默认为纵向(portrait)
    orientation = page_cfg.get("orientation", "portrait")

    # 根据方向设置页面尺寸
    if orientation == "landscape":
        W, H = landscape(A4)  # 横向A4
    else:
        W, H = portrait(A4)   # 纵向A4

    # 创建PDF画布
    c = canvas.Canvas(output, pagesize=(W, H))

    # 获取各部分配置
    header_cfg = cfg.get("header", {})   # 页眉配置
    footer_cfg = cfg.get("footer", {})   # 页脚配置
    modules = cfg.get("modules", [])     # 模块配置

    # 计算各部分高度
    header_h = header_cfg.get("height", 30)  # 页眉高度
    footer_h = footer_cfg.get("height", 20)  # 页脚高度
    # 计算箴言框高度
    quote_box = header_cfg.get("quote_box", None)
    quote_h = quote_box["height"] if quote_box else 0
    # 计算可用的主体区域高度（需要减去箴言框高度）
    usable_h = H - margin * 2 - header_h - quote_h - footer_h

    # Create renderer instance
    renderer = ComponentRenderer(c, CHINESE_FONT)
    
    # 绘制页眉
    renderer.draw_header(margin, H - margin, W - 2 * margin, header_h, header_cfg)
    
    # 绘制箴言框（如果存在）
    if quote_box:
        quote_y = H - margin - header_h - quote_h  # 箴言框的y坐标
        renderer.draw_quote_box(margin, quote_y, W - 2 * margin, quote_h, header_cfg)

    # 绘制主体模块（均匀分布）
    if modules:
        # 获取模块间距，默认为5
        module_spacing = cfg.get("module_spacing", 5)
        # 计算每个模块的高度
        module_h = usable_h / len(modules) - module_spacing
        # 初始化Y坐标(从页眉和箴言框下方开始)
        y = H - margin - header_h - quote_h - module_spacing
        # 遍历所有模块并绘制
        for m in modules:
            renderer.draw_cornell_module(margin, y, W - 2 * margin, module_h, m)
            # 移动Y坐标到下一个模块位置
            y -= module_h + module_spacing

    # 绘制页脚
    renderer.draw_footer(margin, margin, W - 2 * margin, footer_h, footer_cfg)

    # 保存页面并关闭画布
    c.showPage()
    c.save()
    print(f"✅ 笔记本模板已生成: {output}")


# ---------------------------
# CLI 接口
# ---------------------------
if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) < 2:
        print("用法: python notebook_generator.py config.json")
        sys.exit(1)

    # 调用主函数生成笔记本
    generate_notebook(sys.argv[1])