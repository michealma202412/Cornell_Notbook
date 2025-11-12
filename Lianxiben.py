import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math

# --- Page & layout parameters (all units in mm) ---
A4_w_mm, A4_h_mm = 297.0, 210.0  # landscape width x height in mm
binding_width = 15.0             # first column (left) binding margin width in mm (you can change)
num_content_cols = 6
col_sep_style = (0.0, (5.0, 5.0))  # dashed pattern for vertical separators (on in mm units for display)
top_margin = 3.0   # top margin in mm
bottom_margin = 0
left_margin = 6.0   # extra left margin inside binding area
right_margin = 0

# Grid configurations for different notebook types
grid_configs = {
    "幼儿拼音本": {
        "upper_h": 6.0,   # 上格 6 mm
        "middle_h": 10.0, # 中格 10 mm
        "lower_h": 6.0,   # 下格 6 mm
        "intercell_gap": 4.0,
        "description": "字大，适合刚起步"
    },
    "小学拼音本（标准）": {
        "upper_h": 5.0,   # 上格 5 mm
        "middle_h": 8.0,  # 中格 8 mm
        "lower_h": 5.0,   # 下格 5 mm
        "intercell_gap": 4.0,
        "description": "普通拼音、英语练习用"
    },
    "英语抄写本（成人）": {
        "upper_h": 4.0,   # 上格 4 mm
        "middle_h": 6.0,  # 中格 6 mm
        "lower_h": 4.0,   # 下格 4 mm
        "intercell_gap": 0,
        "description": "紧凑，用于速度练习"
    }
}

# Select notebook type (change this to switch between types)
notebook_type = "英语抄写本（成人）"  # Options: "幼儿拼音本", "小学拼音本（标准）", "英语抄写本（成人）"

# Grid cell parameters based on selected type
selected_config = grid_configs[notebook_type]
upper_h = selected_config["upper_h"]
middle_h = selected_config["middle_h"]
lower_h = selected_config["lower_h"]
intercell_gap = selected_config["intercell_gap"]
cell_pitch = upper_h + middle_h + lower_h + intercell_gap

# --- Matplotlib figure setup (convert mm to inches) ---
mm_to_in = 1.0 / 25.4
fig_w_in = A4_w_mm * mm_to_in
fig_h_in = A4_h_mm * mm_to_in
fig = plt.figure(figsize=(fig_w_in, fig_h_in), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, A4_w_mm)
ax.set_ylim(0, A4_h_mm)
ax.set_axis_off()

# Calculate optimal margins to balance top and bottom space
# We want to distribute remaining space equally between top and bottom margins

# Store initial margin values
initial_top_margin = top_margin
initial_bottom_margin = bottom_margin
content_height = A4_h_mm - initial_top_margin - initial_bottom_margin
full_cells = math.floor(content_height / cell_pitch)
used_height = full_cells * cell_pitch
remaining_space = content_height - used_height
top_margin = initial_top_margin + remaining_space / 2
bottom_margin = initial_bottom_margin + remaining_space / 2

# Colors and styles (user-specified)
color_light_gray = "#cccccc"
color_light_blue = "#8fbfff"  # a light blue
sep_color = "black"

# Titles (from right to left across the 7 content columns)
titles_right_to_left = ["day2", "day7", "day15", "day28", "day49", "day1&83"]

# --- Calculate column widths ---
usable_width = A4_w_mm - binding_width - left_margin - right_margin
col_width = usable_width / num_content_cols

# Helper to draw a horizontal line across a specific x-range
def draw_hline(x0, x1, y, color, linestyle='solid', linewidth=0.8):
    ax.add_line(Line2D([x0, x1], [y, y], linewidth=linewidth, color=color, linestyle=linestyle, solid_capstyle='butt'))

# Draw column separators
x_binding_right = binding_width + left_margin
ax.add_line(Line2D([binding_width, binding_width], [0, A4_h_mm], linewidth=0.5, color=sep_color, linestyle='solid'))

for i in range(1, num_content_cols):
    x = binding_width + left_margin + i * col_width
    ax.add_line(Line2D([x, x], [0, A4_h_mm], linewidth=0.6, color=sep_color, linestyle=(0, (3,3))))

# Draw outer borders lightly (optional)
draw_hline(0, A4_w_mm, 0, color_light_gray, linestyle='solid', linewidth=0.6)
draw_hline(0, A4_w_mm, A4_h_mm, color_light_gray, linestyle='solid', linewidth=0.6)
ax.add_line(Line2D([0, 0], [0, A4_h_mm], linewidth=0.6, color=color_light_gray))
ax.add_line(Line2D([A4_w_mm, A4_w_mm], [0, A4_h_mm], linewidth=0.6, color=color_light_gray))

# Draw grid cells in each content column
start_y = A4_h_mm - top_margin
end_y = bottom_margin
y = start_y

x_content_left = binding_width + left_margin
x_content_right = binding_width + left_margin + num_content_cols * col_width

y_pos = start_y
row_count = 0
# Check that we have enough space for at least one cell before entering loop
if y_pos - cell_pitch >= end_y:
    while True:
        line1_y = y_pos
        line2_y = y_pos - upper_h
        line3_y = y_pos - upper_h - middle_h
        line4_y = y_pos - upper_h - middle_h - lower_h

        if line4_y < end_y:
            break

        draw_hline(x_content_left, x_content_right, line1_y, color_light_gray, linestyle=(0, (2,2)), linewidth=0.6)
        draw_hline(x_content_left, x_content_right, line2_y, color_light_blue, linestyle='solid', linewidth=0.8)
        draw_hline(x_content_left, x_content_right, line3_y, color_light_blue, linestyle='solid', linewidth=0.8)
        draw_hline(x_content_left, x_content_right, line4_y, color_light_gray, linestyle='solid', linewidth=0.8)

        y_pos = line4_y - intercell_gap
        row_count += 1

ax.add_line(Line2D([x_content_left, x_content_left], [0, A4_h_mm], linewidth=0.6, color=color_light_gray, linestyle='solid'))
ax.add_line(Line2D([x_content_right, x_content_right], [0, A4_h_mm], linewidth=0.6, color=color_light_gray, linestyle='solid'))

# Write titles at top of each content column from right to left
fontdict = {"fontsize": 9, "ha": "center", "va": "bottom"}
for i in range(num_content_cols):
    col_x0 = binding_width + left_margin + i * col_width
    col_x1 = col_x0 + col_width
    center_x = (col_x0 + col_x1) / 2.0
    idx_from_right = num_content_cols - 1 - i
    title = titles_right_to_left[idx_from_right]
    ax.text(center_x, A4_h_mm - top_margin + 1.5, title, fontdict=fontdict)
#标注装订区域
ax.text(binding_width/2.0, A4_h_mm - top_margin + 1.5, "装订", fontdict={"fontsize":8, "ha":"center", "va":"bottom"}, rotation=90, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

# Save to PDF and PNG - using local directory instead of /mnt/data/
out_pdf = f"four_line_three_grid_{notebook_type}_a4_landscape.pdf"
out_png = f"four_line_three_grid_{notebook_type}_a4_landscape.png"
plt.savefig(out_pdf, bbox_inches='tight', pad_inches=0)
plt.savefig(out_png, bbox_inches='tight', pad_inches=0)
plt.close(fig)