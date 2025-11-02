import json
import sys
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.colors import black, lightgrey, blue
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
            row_heights = [4, 6, 4]
            
        # Calculate how many groups can be drawn
        total_row_height = sum(row_heights)
        n = int(height // total_row_height)
        for i in range(n):
            base_y = y - i * total_row_height
            # Line 1 - light grey dashed line
            c.setStrokeColor(lightgrey)
            c.setDash(1, 2)
            c.line(x, base_y, x + width, base_y)
            # Line 2 - blue solid line
            c.setDash()
            c.setStrokeColor(blue)
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
    def draw_single_line_grid(c, x, y, width, height, line_step=14):
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
        text_padding = config.get("text_padding", 2)
        vertical_padding = config.get("vertical_padding", 3)
        
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
        margin = config.get("field_margin", 5)
        cursor_x = x + margin
        fields = config.get("fields", [])
        
        if fields:
            field_spacing = config.get("field_spacing", 5)
            total_field_width = width - 2 * margin - (len(fields) - 1) * field_spacing
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
            
            box_y = y - field_height + config.get("field_vertical_padding", 6)
            
            field_config = {
                "text_padding": text_padding,
                "vertical_padding": vertical_padding
            }
            self.draw_text_box(cursor_x, box_y, field_width, field_height, text, field_config, 
                              alignment=text_alignment, vertical_alignment=vertical_alignment)
            
            field_spacing = config.get("field_spacing", 5)
            cursor_x += field_width + field_spacing

    def draw_quote_box(self, x, y, width, height, config):
        """
        Draw the quote area (L0[1]) with daily quote text (L1[0])
        """
        self.canvas.setFont(self.font, 12)
        quote = config.get("quote_box", None)
        if not quote:
            return
        
        quote_label_padding = config.get("quote_label_padding", 5)
        quote_vertical_padding = quote.get("vertical_padding", 3)
        
        quote_text = quote["label"] + ":"
        quote_text_width = self.canvas.stringWidth(quote_text, self.font, 12)
        quote_text_height = 12
        
        quote_box_height = max(quote["height"], quote_text_height + 2 * quote_vertical_padding)
        
        quote_config = {
            "text_padding": quote_label_padding,
            "vertical_padding": quote_vertical_padding
        }
        self.draw_text_box(x, y, width, quote_box_height, quote_text, quote_config, 
                          alignment="left", vertical_alignment="middle")

    def draw_footer(self, x, y, width, height, config):
        """
        Draw the footer area (L0[3]) with review boxes (L1[0-5])
        """
        self.canvas.setStrokeColor(black)
        self.canvas.rect(x, y, width, height, stroke=1, fill=0)
        self.canvas.setFont(self.font, 12)
        
        review_boxes = config.get("review_boxes", [])
        cursor_x = x + config.get("review_label_left_margin", 5)
        cursor_x += config.get("review_text_right_spacing", 40)
        
        remaining_space = width - (cursor_x - x)
        if len(review_boxes) > 0:
            box_config_width = config.get("review_box_width", 15)
            if box_config_width == "auto":
                total_config_width = 0
            else:
                total_config_width = box_config_width * len(review_boxes)
                remaining_space -= total_config_width
            if len(review_boxes) > 1:
                uniform_spacing = remaining_space / (len(review_boxes) - 1)
            else:
                uniform_spacing = config.get("review_box_spacing", 10)
        else:
            uniform_spacing = config.get("review_box_spacing", 10)
        
        for i, label in enumerate(review_boxes):
            box_w = config.get("review_box_width", 15)
            box_height = config.get("review_box_height", 5)
            box_top_margin = config.get("review_box_top_margin", 10)
            text_padding = config.get("review_box_text_padding", 2)
            
            text_width = self.canvas.stringWidth(label, self.font, 12)
            text_height = 12
            
            if box_w == "auto":
                box_w = max(15, text_width + 2 * text_padding)
            else:
                box_w = max(box_w, text_width + 2 * text_padding)
            box_height = max(box_height, text_height + 2 * text_padding)
                
            box_y = y + box_top_margin
            
            box_config = {
                "text_padding": text_padding,
                "vertical_padding": text_padding
            }
            text_alignment = config.get("review_text_alignment", "center")
            self.draw_text_box(cursor_x, box_y, box_w, box_height, label, box_config, 
                              alignment=text_alignment, vertical_alignment="middle")
            
            spacing = uniform_spacing if len(review_boxes) > 1 else config.get("review_box_spacing", 10)
            cursor_x += box_w + spacing

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
        
        theme_h = config.get("theme_height", 14)
        summary_h = config.get("summary_height", 14)
        keyword_width_ratio = config.get("keyword_width_ratio", 0.3)
        keyword_w = width * keyword_width_ratio
        line_style = config.get("line_style", "single_line")

        # Draw outer border
        self.canvas.setStrokeColor(black)
        self.canvas.rect(x, y - height, width, height, stroke=1, fill=0)

        # Draw internal dividing lines
        self.canvas.line(x, y - theme_h, x + width, y - theme_h)  # Title bottom
        self.canvas.line(x, y - height + summary_h, x + width, y - height + summary_h)  # Summary top
        self.canvas.line(x + keyword_w, y - theme_h, x + keyword_w, y - height + summary_h)  # Keywords right
        
        # Divide summary area into two rows
        summary_mid_y = y - height + summary_h/2
        self.canvas.line(x, summary_mid_y, x + width, summary_mid_y)

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

    def _draw_four_line_three_grid_layout(self, grid_renderer, x, y, width, height, 
                                        theme_h, summary_h, keyword_w, config):
        """
        Draw four-line three-grid pattern in all sections
        """
        line_spacing = config.get("grid_line_spacing", 6)
        row_heights = config.get("grid_row_heights", [4, 6, 4])
        
        # Notes area
        offset_x = keyword_w + config.get("grid_offset_x", 2)
        offset_y = theme_h + config.get("grid_offset_y", 4)
        width_reduction = keyword_w + config.get("grid_width_reduction", 4)
        height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x + offset_x, y - offset_y, 
            width - width_reduction, height - height_reduction, 
            line_spacing, row_heights)
        
        # Keywords area
        kw_offset_y = theme_h + config.get("grid_offset_y", 4)
        kw_height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - kw_offset_y, 
            keyword_w - config.get("grid_offset_x", 2) * 2, 
            height - kw_height_reduction, line_spacing, row_heights)
        
        # Summary area (two rows)
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
        
        # Title area
        theme_offset_y = theme_h - config.get("grid_offset_y", 4)
        grid_renderer.draw_four_line_three_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - theme_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            theme_h - config.get("grid_offset_y", 4) * 2, line_spacing, row_heights)

    def _draw_single_line_layout(self, grid_renderer, x, y, width, height, 
                               theme_h, summary_h, keyword_w, config):
        """
        Draw single horizontal lines in all sections
        """
        step = config.get("line_step", 8)
        offset_y = theme_h + config.get("grid_offset_y", 4)
        bottom_margin = summary_h + config.get("grid_offset_y", 4)
        yy = y - offset_y
        
        # Notes area
        while yy > y - height + bottom_margin:
            self.canvas.setStrokeColor(lightgrey)
            self.canvas.line(x + keyword_w + config.get("grid_offset_x", 2), yy, 
                            x + width - config.get("grid_offset_x", 2), yy)
            yy -= step
            
        # Keywords area
        kw_y = y - theme_h - config.get("grid_offset_y", 4)
        kw_bottom = y - height + summary_h + config.get("grid_offset_y", 4)
        while kw_y > kw_bottom:
            self.canvas.setStrokeColor(lightgrey)
            self.canvas.line(x + config.get("grid_offset_x", 2), kw_y, 
                            x + keyword_w - config.get("grid_offset_x", 2), kw_y)
            kw_y -= step
            
        # Summary area (two rows)
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
            
        # Title area
        theme_y = y - theme_h + config.get("grid_offset_y", 4)
        while theme_y < y - config.get("grid_offset_y", 4):
            self.canvas.setStrokeColor(lightgrey)
            self.canvas.line(x + config.get("grid_offset_x", 2), theme_y, 
                            x + width - config.get("grid_offset_x", 2), theme_y)
            theme_y += step

    def _draw_dotted_grid_layout(self, grid_renderer, x, y, width, height, 
                               theme_h, summary_h, keyword_w, config):
        """
        Draw dotted grid pattern in all sections
        """
        dot_spacing = config.get("grid_dot_spacing", 20)
        
        # Notes area
        offset_x = keyword_w + config.get("grid_offset_x", 2)
        offset_y = theme_h + config.get("grid_offset_y", 4)
        width_reduction = keyword_w + config.get("grid_width_reduction", 4)
        height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        
        grid_renderer.draw_dotted_grid(
            self.canvas, x + offset_x, y - offset_y,
            width - width_reduction, height - height_reduction, dot_spacing)
        
        # Keywords area
        kw_offset_y = theme_h + config.get("grid_offset_y", 4)
        kw_height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        grid_renderer.draw_dotted_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - kw_offset_y,
            keyword_w - config.get("grid_offset_x", 2) * 2,
            height - kw_height_reduction, dot_spacing)
        
        # Summary area
        sum_offset_y = height - summary_h + config.get("grid_offset_y", 4)
        grid_renderer.draw_dotted_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - sum_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            summary_h - config.get("grid_offset_y", 4) * 2, dot_spacing)
        
        # Title area
        theme_offset_y = theme_h - config.get("grid_offset_y", 4)
        grid_renderer.draw_dotted_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - theme_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            theme_h - config.get("grid_offset_y", 4) * 2, dot_spacing)

    def _draw_english_grid_layout(self, grid_renderer, x, y, width, height, 
                                theme_h, summary_h, keyword_w, config):
        """
        Draw English writing practice grid in all sections
        """
        line_spacing = config.get("grid_line_spacing", 8)
        
        # Notes area
        offset_x = keyword_w + config.get("grid_offset_x", 2)
        offset_y = theme_h + config.get("grid_offset_y", 4)
        width_reduction = keyword_w + config.get("grid_width_reduction", 4)
        height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        
        grid_renderer.draw_english_grid(
            self.canvas, x + offset_x, y - offset_y,
            width - width_reduction, height - height_reduction, line_spacing)
        
        # Keywords area
        kw_offset_y = theme_h + config.get("grid_offset_y", 4)
        kw_height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        grid_renderer.draw_english_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - kw_offset_y,
            keyword_w - config.get("grid_offset_x", 2) * 2,
            height - kw_height_reduction, line_spacing)
        
        # Summary area
        sum_offset_y = height - summary_h + config.get("grid_offset_y", 4)
        grid_renderer.draw_english_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - sum_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            summary_h - config.get("grid_offset_y", 4) * 2, line_spacing)
        
        # Title area
        theme_offset_y = theme_h - config.get("grid_offset_y", 4)
        grid_renderer.draw_english_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - theme_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            theme_h - config.get("grid_offset_y", 4) * 2, line_spacing)

    def _draw_tianzige_grid_layout(self, grid_renderer, x, y, width, height, 
                                 theme_h, summary_h, keyword_w, config):
        """
        Draw Tianzige grid in all sections
        """
        cell_size = config.get("grid_cell_size", 30)
        
        # Notes area
        offset_x = keyword_w + config.get("grid_offset_x", 2)
        offset_y = theme_h + config.get("grid_offset_y", 4)
        width_reduction = keyword_w + config.get("grid_width_reduction", 4)
        height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        
        grid_renderer.draw_tianzige_grid(
            self.canvas, x + offset_x, y - offset_y,
            width - width_reduction, height - height_reduction, cell_size)
        
        # Keywords area
        kw_offset_y = theme_h + config.get("grid_offset_y", 4)
        kw_height_reduction = theme_h + summary_h + config.get("grid_height_reduction", 6)
        grid_renderer.draw_tianzige_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - kw_offset_y,
            keyword_w - config.get("grid_offset_x", 2) * 2,
            height - kw_height_reduction, cell_size)
        
        # Summary area
        sum_offset_y = height - summary_h + config.get("grid_offset_y", 4)
        grid_renderer.draw_tianzige_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - sum_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            summary_h - config.get("grid_offset_y", 4) * 2, cell_size)
        
        # Title area
        theme_offset_y = theme_h - config.get("grid_offset_y", 4)
        grid_renderer.draw_tianzige_grid(
            self.canvas, x + config.get("grid_offset_x", 2), y - theme_offset_y,
            width - config.get("grid_offset_x", 2) * 2,
            theme_h - config.get("grid_offset_y", 4) * 2, cell_size)


def generate_notebook(config_path):
    """
    Generate Cornell notebook PDF based on configuration
    """
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    output = cfg.get("output", "notebook.pdf")
    page_cfg = cfg.get("page", {})
    margin = page_cfg.get("margin", 20)
    orientation = page_cfg.get("orientation", "portrait")

    if orientation == "landscape":
        W, H = landscape(A4)
    else:
        W, H = portrait(A4)

    c = canvas.Canvas(output, pagesize=(W, H))

    header_cfg = cfg.get("header", {})
    footer_cfg = cfg.get("footer", {})
    modules = cfg.get("modules", [])

    header_h = header_cfg.get("height", 30)
    footer_h = footer_cfg.get("height", 20)
    quote_box = header_cfg.get("quote_box", None)
    quote_h = quote_box["height"] if quote_box else 0
    usable_h = H - margin * 2 - header_h - quote_h - footer_h

    renderer = ComponentRenderer(c, CHINESE_FONT)
    
    # Draw header (L0[0])
    renderer.draw_header(margin, H - margin, W - 2 * margin, header_h, header_cfg)
    
    # Draw quote area (L0[1])
    if quote_box:
        quote_y = H - margin - header_h - quote_h
        renderer.draw_quote_box(margin, quote_y, W - 2 * margin, quote_h, header_cfg)

    # Draw Cornell modules (L0[2])
    if modules:
        module_spacing = cfg.get("module_spacing", 5)
        module_h = usable_h / len(modules) - module_spacing
        y = H - margin - header_h - quote_h - module_spacing
        for m in modules:
            renderer.draw_cornell_module(margin, y, W - 2 * margin, module_h, m)
            y -= module_h + module_spacing

    # Draw footer (L0[3])
    renderer.draw_footer(margin, margin, W - 2 * margin, footer_h, footer_cfg)

    c.showPage()
    c.save()
    print(f"✅ Notebook template generated: {output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Cornell_gen_1102.py config.json")
        sys.exit(1)

    generate_notebook(sys.argv[1])