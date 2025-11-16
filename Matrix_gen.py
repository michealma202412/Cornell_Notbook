import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math
import json
import sys
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfgen import canvas
from Cornell_gen_1102 import AreaMatrixRenderer, CHINESE_FONT, PAPER_SIZES, MM_TO_POINTS

class MatrixNotebookGenerator:
    """
    Generator for matrix-style notebooks with configurable cells
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.font = CHINESE_FONT
    
    def generate(self):
        """
        Generate matrix notebook PDF based on configuration
        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        output = cfg.get("output", "matrix_notebook.pdf")
        page_cfg = cfg.get("page_format", {})
        page_size_name = page_cfg.get("size", "A4")
        page_size = PAPER_SIZES.get(page_size_name, A4) 
        orientation = page_cfg.get("orientation", "portrait")
        if orientation == "landscape":
            W, H = landscape(page_size)
        else:
            W, H = portrait(page_size)

        c = canvas.Canvas(output, pagesize=(W, H))
        
        # Get margins
        margin = page_cfg.get("margin", 20)
        
        # Matrix configuration
        matrix_cfg = cfg.get("matrix", {})
        rows = matrix_cfg.get("rows", 10)
        cols = matrix_cfg.get("cols", 6)
        cell_defaults = matrix_cfg.get("cell_defaults", {})
        special_cells = matrix_cfg.get("cells", [])
        
        # Create a map of special cell configurations
        cell_config_map = {}
        for cell in special_cells:
            row = cell["row"]
            col = cell["col"]
            cell_config_map[(row, col)] = cell["config"]
        
        # Calculate cell dimensions
        content_width = W - 2 * margin
        content_height = H - 2 * margin
        cell_width = content_width / cols
        cell_height = content_height / rows
        
        # Create renderer
        renderer = AreaMatrixRenderer(c, self.font)
        
        # Draw all cells
        for row in range(rows):
            for col in range(cols):
                # Calculate cell position
                x = margin + col * cell_width
                y = H - margin - (row + 1) * cell_height
                
                # Get configuration for this cell
                config = cell_defaults.copy()
                if (row, col) in cell_config_map:
                    # Merge special configuration with defaults
                    config.update(cell_config_map[(row, col)])
                
                # Render the cell
                renderer.draw(x, y, cell_width, cell_height, config)
        
        c.showPage()
        c.save()
        print(f"✅ Matrix notebook generated: {output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Matrix_gen.py Matrix_cfg.json")
        sys.exit(1)

    generator = MatrixNotebookGenerator(sys.argv[1])
    generator.generate()