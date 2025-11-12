import json
import sys
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.colors import black, lightgrey, blue, lightblue
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register a font that supports Chinese characters
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

# Define standard paper sizes for reference
PAPER_SIZES = {
    'A0': (2384, 3370),
    'A1': (1684, 2384),
    'A2': (1191, 1684),
    'A3': (842, 1191),
    'A4': (595, 842),
    'A5': (420, 595),
    'B0': (2835, 4008),
    'B1': (2004, 2835),
    'B2': (1417, 2004),
    'B3': (1001, 1417),
    'B4': (709, 1001),
    'B5': (499, 709)
}

# Conversion factor from mm to points (1 mm = 2.83464566929134 points)
MM_TO_POINTS = 2.83464566929134

class GridRenderer:
    """
    Handles rendering of different grid types based on struct.md specifications
    """
    
    @staticmethod
    def draw_four_line_three_grid(c, x, y, width, height, line_spacing=6, row_heights=None):
        """
        Draw four-line three-grid pattern (commonly used for Chinese pinyin)
        """
        if row_heights is None:
            row_heights = [3, 3, 3]
            
        # Calculate how many groups can be drawn
        total_row_height = sum(row_heights)
        n = int(height // total_row_height)
        for i in range(n):
            base_y = y - i * total_row_height
            # Line 1 - light grey dashed line
            c.setStrokeColor(lightgrey)
            # c.setDash(1, 2)
            c.line(x, base_y, x + width, base_y)
            # Line 2 - blue dash line
            #c.setDash(1,2)
            c.setStrokeColor(lightblue)
            c.line(x, base_y - row_heights[0], x + width, base_y - row_heights[0])
            # Line 3 - blue solid line
            c.line(x, base_y - row_heights[0] - row_heights[1], x + width, base_y - row_heights[0] - row_heights[1])
            # Line 4 - light grey solid line
            c.setStrokeColor(lightgrey)
            c.line(x, base_y - row_heights[0] - row_heights[1] - row_heights[2], 
                   x + width, base_y - row_heights[0] - row_heights[1] - row_heights[2])

    @staticmethod
    def draw_dotted_grid(c, x, y, width, height, dot_spacing=20):
        """
        Draw dotted grid pattern
        """
        c.setFillColor(lightgrey)
        radius = 0.5
        rows = int(height // dot_spacing) + 1
        cols = int(width // dot_spacing) + 1
        for row in range(rows):
            for col in range(cols):
                dot_x = x + col * dot_spacing
                dot_y = y - row * dot_spacing
                c.circle(dot_x, dot_y, radius, stroke=0, fill=1)
        c.setFillColor(black)

    @staticmethod
    def draw_english_grid(c, x, y, width, height, line_spacing=8):
        """
        Draw English writing practice grid (three-line grid)
        """
        n = int(height // line_spacing)
        for i in range(n):
            base_y = y - i * line_spacing
            # Baseline - black solid line
            c.setStrokeColor(black)
            c.setDash()
            c.line(x, base_y, x + width, base_y)
            # Middle line - grey dashed line
            c.setStrokeColor(lightgrey)
            c.setDash(2, 2)
            c.line(x, base_y - line_spacing/2, x + width, base_y - line_spacing/2)
            # Top line - grey solid line
            c.setStrokeColor(lightgrey)
            c.setDash()
            c.line(x, base_y - line_spacing, x + width, base_y - line_spacing)
        c.setStrokeColor(black)
        c.setDash()

    @staticmethod
    def draw_tianzige_grid(c, x, y, width, height, cell_size=30):
        """
        Draw Tianzige grid (traditional Chinese character practice grid)
        """
        rows = int(height // cell_size)
        cols = int(width // cell_size)
        for row in range(rows):
            for col in range(cols):
                cell_x = x + col * cell_size
                cell_y = y - row * cell_size
                # Draw outer box
                c.rect(cell_x, cell_y - cell_size, cell_size, cell_size)
                # Draw cross lines
                c.line(cell_x, cell_y - cell_size/2, cell_x + cell_size, cell_y - cell_size/2)
                c.line(cell_x + cell_size/2, cell_y - cell_size, cell_x + cell_size/2, cell_y)

    @staticmethod
    def draw_single_line_grid(c, x, y, width, height, line_step):
        """
        Draw single horizontal lines for regular note-taking
        """
        yy = y
        while yy > y - height:
            c.setStrokeColor(lightgrey)
            c.line(x, yy, x + width, yy)
            yy -= line_step


class ComponentRenderer:
    """
    Handles rendering of different notebook components based on struct.md hierarchy
    """
    
    def __init__(self, canvas, font):
        self.canvas = canvas
        self.font = font
        
    def draw_text_box(self, x, y, width, height, text, config, alignment="left", vertical_alignment="top"):
        """
        Draw a box with text, following dynamic sizing rules from struct.md
        """
        # Draw box border
        if config.get("border_enabled", True):
            self.canvas.rect(x, y, width, height, stroke=1, fill=0)
        
        # Get text dimensions
        text_width = self.canvas.stringWidth(text, self.font, 12)
        text_height = 12
        
        # Get padding configuration
        text_padding = config.get("text_padding", 0)
        vertical_padding = config.get("vertical_padding", 0)
        
        # Calculate Y position based on vertical alignment
        if vertical_alignment == "top":
            text_y = y + height - vertical_padding - text_height
        elif vertical_alignment == "middle":
            text_y = y + (height / 2) - (text_height / 2)
        else:  # bottom
            text_y = y + vertical_padding
        
        # Calculate X position based on horizontal alignment
        if alignment == "left":
            text_x = x + text_padding
        elif alignment == "center":
            text_x = x + (width / 2) - (text_width / 2)
        else:  # right
            text_x = x + width - text_padding - text_width
        
        # Draw text
        self.canvas.drawString(text_x, text_y, text)
        
        return width, height

    def draw_header(self, x, y, width, height, config):
        """
        Draw the header area (L0[0]) with fields (L1[0-n])
        """
        self.canvas.setFont(self.font, 12)
        field_margin = config.get("field_margin", 0)
        cursor_x = x + field_margin
        fields = config.get("fields", [])
        
        # Draw header border only if enabled
        if config.get("border_enabled", True):
            self.canvas.rect(x, y, width, height, stroke=1, fill=0)
        
        if fields:
            field_spacing = config.get("field_spacing", 0)
            total_field_width = width - 2 * field_margin - (len(fields) - 1) * field_spacing
            uniform_field_width = total_field_width / len(fields)
        
        for field in fields:
            text_alignment = field.get("text_alignment", "left")
            text_padding = field.get("text_padding", 2)
            vertical_alignment = field.get("vertical_alignment", "top")
            vertical_padding = field.get("vertical_padding", 3)
            
            text = field["label"] + ":"
            text_width = self.canvas.stringWidth(text, self.font, 12)
            text_height = 12
            
            # Dynamic sizing based on text
            field_width = max(uniform_field_width, text_width + 2 * text_padding)
            field_height = max(20, text_height + 2 * vertical_padding)
            
            box_y = y - field_height + config.get("field_vertical_padding", 0)
            
            field_config = {
                "text_padding": text_padding,
                "vertical_padding": vertical_padding,
                "border_enabled": field.get("border_enabled", True)  # Use field-specific border setting
            }
            self.draw_text_box(cursor_x, box_y, field_width, field_height, text, field_config, 
                              alignment=text_alignment, vertical_alignment=vertical_alignment)
            
            field_spacing = config.get("field_spacing", 0)
            cursor_x += field_width + field_spacing

    def draw_quote_box(self, x, y, width, height, config):
        """
        Draw the quote area (L0[1]) with daily quote text (L1[0])
        """
        self.canvas.setFont(self.font, 12)
        quote = config.get("quote_box", None)
        if not quote:
            return
        
        quote_label_padding = config.get("quote_label_padding", 0)
        quote_vertical_padding = quote.get("vertical_padding", 0)
        
        quote_text = quote["label"] + ":"
        quote_text_width = self.canvas.stringWidth(quote_text, self.font, 12)
        quote_text_height = 12
        
        # Use the height from the config parameter (which is the quote area height)
        # rather than trying to access a non-existent quote["height"]
        quote_box_height = max(height, quote_text_height + 2 * quote_vertical_padding)
        
        # Draw quote box border only if enabled
        if config.get("border_enabled", True):
            self.canvas.rect(x, y, width, quote_box_height, stroke=1, fill=0)
        
        quote_config = {
            "text_padding": quote_label_padding,
            "vertical_padding": quote_vertical_padding
        }
        self.draw_text_box(x, y, width, quote_box_height, quote_text, quote_config, 
                          alignment="left", vertical_alignment="top")

    def draw_footer(self, x, y, width, height, config):
        """
        Draw the footer area (L0[3]) with review boxes (L1[0-5])
        """
        # Draw footer border only if enabled
        if config.get("border_enabled", True):
            self.canvas.setStrokeColor(black)
            self.canvas.rect(x, y, width, height, stroke=1, fill=0)
        self.canvas.setFont(self.font, 12)
        
        review_boxes = config.get("review_boxes", [])
        if len(review_boxes) > 0:
            # Calculate available space for boxes (total width minus margins)
            available_space = width
            box_width = available_space / len(review_boxes)
            
            # Position boxes from the left edge
            cursor_x = x
            
            for i, label in enumerate(review_boxes):
                # 使用 footer 的 height 作为 review box 的高度
                box_height = height
                box_top_margin = config.get("review_box_top_margin", 0)
                text_padding = config.get("review_box_text_padding", 0)
                
                text_width = self.canvas.stringWidth(label, self.font, 12)
                text_height = 12
                
                # Ensure box is wide enough for text
                box_w = max(box_width, text_width + 2 * text_padding)
                #box_height = max(box_height, text_height + 2 * text_padding)
 
                box_y = y + box_top_margin
                
                box_config = {
                    "text_padding": text_padding,
                    "vertical_padding": text_padding,
                    "border_enabled": False  # Disable border for footer text boxes
                }
                text_alignment = config.get("review_text_alignment", "center")
                self.draw_text_box(cursor_x, box_y, box_w, box_height, label, box_config, 
                                  alignment=text_alignment, vertical_alignment="middle")
                
                # Move cursor to next position (boxes tightly packed)
                cursor_x += box_w

    def draw_cornell_module(self, x, y, width, height, config):
        """
        Draw the Cornell note area (L0[2]) with its subdivisions:
        - Title section (L1[0])
        - Content section (L1[1]) with:
          - Keywords section (L2[0])
          - Notes section (L2[1])
        - Summary section (L1[2])
        """
        self.canvas.setFont(self.font, 12)
        
        # Convert mm values to points
        step = config.get("line_step_mm") * MM_TO_POINTS
        theme_h = config.get("theme_height_mm", 0) * MM_TO_POINTS
        theme_h = theme_h
        summary_h = config.get("summary_height_mm", 0) * MM_TO_POINTS
        keyword_width_ratio = config.get("keyword_width_ratio", 0.3)
        keyword_w = width * keyword_width_ratio
        line_style = config.get("line_style", "single_line")
        label_padding = config.get("label_padding", 0)  # 新增配置项
        # Draw outer border only if enabled
        if config.get("border_enabled", True):
            self.canvas.setStrokeColor(black)
            self.canvas.rect(x, y - height, width, height, stroke=1, fill=0)

        # Draw section labels
        # Title section label
        if theme_h > 0:
            title_label = config.get("title_label", "")
            title_label_x = x + label_padding
            
            # 调整标题标签的Y坐标，使其与第一行格线对齐并居中
            title_label_y = y - theme_h + (theme_h) / 4  # 居中对齐
            self.canvas.drawString(title_label_x, title_label_y, title_label)
        
        # Keywords section label
        keyword_label = config.get("keyword_label", "")
        keyword_label_x = x + label_padding
        
        # 调整关键词标签的Y坐标，使其与第一行格线对齐
        keyword_label_y = y - theme_h - step + step / 4
        if theme_h > 0:
            self.canvas.drawString(keyword_label_x, keyword_label_y, keyword_label)
        
        # Summary section label
        if summary_h > 0:
            summary_label = config.get("summary_label", "总结")
            summary_label_x = x + label_padding
            summary_label_y = y - height + summary_h - step + step / 4
            self.canvas.drawString(summary_label_x, summary_label_y, summary_label)

        # Draw grid lines based on configuration
        grid_renderer = GridRenderer()
        
        if line_style == "four_line_three_grid":
            self._draw_four_line_three_grid_layout(grid_renderer, x, y, width, height, 
                                                 theme_h, summary_h, keyword_w, config)
        elif line_style == "single_line":
            self._draw_single_line_layout(grid_renderer, x, y, width, height, 
                                        theme_h, summary_h, keyword_w, config)
        elif line_style == "dotted":
            self._draw_dotted_grid_layout(grid_renderer, x, y, width, height, 
                                        theme_h, summary_h, keyword_w, config)
        elif line_style == "english_grid":
            self._draw_english_grid_layout(grid_renderer, x, y, width, height, 
                                         theme_h, summary_h, keyword_w, config)
        elif line_style == "tianzige":
            self._draw_tianzige_grid_layout(grid_renderer, x, y, width, height, 
                                          theme_h, summary_h, keyword_w, config)
        # blank layout requires no grid drawing

        # 设置分割线颜色为黑色
        self.canvas.setStrokeColor(black)

        # Draw internal dividing lines - 确保与行格线对齐
        # 标题区底部线：从标题区底部开始
        if theme_h > 0:
            self.canvas.line(x, y - theme_h, x + width, y - theme_h)  # Title bottom
        
        # 总结区顶部线：从总结区顶部开始
        if summary_h > 0:
            self.canvas.line(x, y - height + summary_h, x + width, y - height + summary_h)  # Summary top
        
        # 关键词区右侧线：从关键词区右侧开始，垂直方向对齐
        self.canvas.line(x + keyword_w, y - theme_h, x + keyword_w, y - height + summary_h)  # Keywords right

    def _draw_four_line_three_grid_layout(self, grid_renderer, x, y, width, height, 
                                        theme_h, summary_h, keyword_w, config):
        """
        Draw four-line three-grid pattern in all sections
        """
        # Convert mm values to points
        line_spacing = config.get("grid_line_spacing_mm", 0) * MM_TO_POINTS
        row_heights = [h * MM_TO_POINTS for h in config.get("grid_row_heights_mm", [3, 3, 3])]
        
        # Notes area
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x + keyword_w, y - theme_h,
            width - keyword_w, height - theme_h - summary_h, 
            line_spacing, row_heights)
        
        # Keywords area
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x, y - theme_h,
            keyword_w,
            height - theme_h - summary_h, line_spacing, row_heights)
        
        # Summary area (two rows)
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x, y - (height - summary_h),
            width,
            summary_h/2, line_spacing, row_heights)
        
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x, y - (height - summary_h/2),
            width,
            summary_h/2, line_spacing, row_heights)
        
        # Title area
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x, y - theme_h,
            width,
            theme_h, line_spacing, row_heights)

    def _draw_single_line_layout(self, grid_renderer, x, y, width, height, 
                               theme_h, summary_h, keyword_w, config):
        """
        Draw single horizontal lines in all sections
        """
        # Convert mm values to points
        step = config.get("line_step_mm", 0) * MM_TO_POINTS
        
        # Notes area
        grid_renderer.draw_single_line_grid(
            self.canvas, x + keyword_w, y - theme_h,
            width - keyword_w, height - theme_h - summary_h, step)
        
        # Keywords area
        grid_renderer.draw_single_line_grid(
            self.canvas, x, y - theme_h,
            keyword_w,
            height - theme_h - summary_h, step)
        
        # Summary area
        grid_renderer.draw_single_line_grid(
            self.canvas, x, y - (height - summary_h),
            width,
            summary_h, step)
        
        # Title area
        grid_renderer.draw_single_line_grid(
            self.canvas, x, y - theme_h,
            width,
            theme_h, step)

    def _draw_dotted_grid_layout(self, grid_renderer, x, y, width, height, 
                               theme_h, summary_h, keyword_w, config):
        """
        Draw dotted grid pattern in all sections
        """
        # Convert mm values to points
        dot_spacing = config.get("grid_dot_spacing_mm", 20) * MM_TO_POINTS
        
        # Notes area
        grid_renderer.draw_dotted_grid(
            self.canvas, x + keyword_w, y - theme_h,
            width - keyword_w, height - theme_h - summary_h, dot_spacing)
        
        # Keywords area
        grid_renderer.draw_dotted_grid(
            self.canvas, x, y - theme_h,
            keyword_w,
            height - theme_h - summary_h, dot_spacing)
        
        # Summary area
        grid_renderer.draw_dotted_grid(
            self.canvas, x, y - (height - summary_h),
            width,
            summary_h, dot_spacing)
        
        # Title area
        grid_renderer.draw_dotted_grid(
            self.canvas, x, y - theme_h,
            width,
            theme_h, dot_spacing)

    def _draw_english_grid_layout(self, grid_renderer, x, y, width, height, 
                                theme_h, summary_h, keyword_w, config):
        """
        Draw English writing practice grid in all sections
        """
        # Convert mm values to points
        line_spacing = config.get("grid_line_spacing_mm", 8) * MM_TO_POINTS
        
        # Notes area
        grid_renderer.draw_english_grid(
            self.canvas, x + keyword_w, y - theme_h,
            width - keyword_w, height - theme_h - summary_h, line_spacing)
        
        # Keywords area
        grid_renderer.draw_english_grid(
            self.canvas, x, y - theme_h,
            keyword_w,
            height - theme_h - summary_h, line_spacing)
        
        # Summary area
        grid_renderer.draw_english_grid(
            self.canvas, x, y - (height - summary_h),
            width,
            summary_h, line_spacing)
        
        # Title area
        grid_renderer.draw_english_grid(
            self.canvas, x, y - theme_h,
            width,
            theme_h, line_spacing)

    def _draw_tianzige_grid_layout(self, grid_renderer, x, y, width, height, 
                                 theme_h, summary_h, keyword_w, config):
        """
        Draw Tianzige grid in all sections
        """
        # Convert mm values to points
        cell_size = config.get("grid_cell_size_mm", 30) * MM_TO_POINTS
        
        # Notes area
        grid_renderer.draw_tianzige_grid(
            self.canvas, x + keyword_w, y - theme_h,
            width - keyword_w, height - theme_h - summary_h, cell_size)
        
        # Keywords area
        grid_renderer.draw_tianzige_grid(
            self.canvas, x, y - theme_h,
            keyword_w,
            height - theme_h - summary_h, cell_size)
        
        # Summary area
        grid_renderer.draw_tianzige_grid(
            self.canvas, x, y - (height - summary_h),
            width,
            summary_h, cell_size)
        
        # Title area
        grid_renderer.draw_tianzige_grid(
            self.canvas, x, y - theme_h,
            width,
            theme_h, cell_size)


def generate_notebook(config_path):
    """
    Generate Cornell notebook PDF based on configuration
    """
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    output = cfg.get("output", "notebook.pdf")
    page_cfg = cfg.get("page", {})
    page_size_name = page_cfg.get("size", "A4")
    page_size = PAPER_SIZES.get(page_size_name, A4) 
    orientation = page_cfg.get("orientation", "portrait")
    if orientation == "landscape":
        W, H = landscape(page_size)
    else:
        W, H = portrait(page_size)

    c = canvas.Canvas(output, pagesize=(W, H))

    header_cfg = cfg.get("header", {})
    footer_cfg = cfg.get("footer", {})
    modules = cfg.get("modules", [])
    # Get quote configuration separately
    quote_cfg = cfg.get("quote", {})

    header_h = header_cfg.get("height_mm", 0) * MM_TO_POINTS
    footer_h = footer_cfg.get("height_mm", 0) * MM_TO_POINTS
    # Get quote height from quote config in mm and convert to points
    quote_h_mm = quote_cfg.get("height_mm", 0)
    quote_h = quote_h_mm * MM_TO_POINTS

    step = page_cfg.get("line_step_mm", 9) * MM_TO_POINTS
    renderer = ComponentRenderer(c, CHINESE_FONT)

    # Adjust margins with binding margin consideration
    # For binding, we add extra base_margin to both sides to allow for proper hole punching/clipboarding
    # Support for individual binding margins
    base_margin = page_cfg.get("base_margin", 0)
    left_binding_margin = page_cfg.get("left_binding_margin", 0)
    right_binding_margin = page_cfg.get("right_binding_margin", 0)
    top_binding_margin = page_cfg.get("top_binding_margin", 0)
    bottom_binding_margin = page_cfg.get("bottom_binding_margin", 0)

    left_margin = left_binding_margin + base_margin
    right_margin = right_binding_margin + base_margin
    top_margin = top_binding_margin + base_margin
    bottom_margin = bottom_binding_margin + base_margin
    usable_h = H - top_margin - bottom_margin - header_h - quote_h - footer_h

    # Draw header (L0[0])
    renderer.draw_header(left_margin, H - top_margin, W - left_margin - right_margin, header_h, header_cfg)

    # Draw quote area (L0[1]) - now handled separately from header
    if quote_cfg:
        quote_y = H - top_margin - header_h - quote_h
        renderer.draw_quote_box(left_margin, quote_y, W - left_margin - right_margin, quote_h, quote_cfg)

    # Draw Cornell modules (L0[2])
    if modules:
        Unused_space = usable_h - (usable_h // (step * len(modules))) * (step * len(modules))
        module_h = (usable_h // (step * len(modules))) * step
        y = H - top_margin - header_h - quote_h
        for m in modules:
            renderer.draw_cornell_module(left_margin, y, W - left_margin - right_margin, module_h, m)
            y -= module_h

    # Draw footer (L0[3])
    renderer.draw_footer(left_margin, bottom_margin, W - left_margin - right_margin, footer_h, footer_cfg)

    c.showPage()
    c.save()
    print(f"✅ Notebook template generated: {output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Cornell_gen_1102.py config.json")
        sys.exit(1)

    generate_notebook(sys.argv[1])
