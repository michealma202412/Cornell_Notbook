# Cornell Notebook Layout Structure

This document defines the hierarchical structure for organizing rectangular areas in a Cornell-style notebook. Each level represents a grouping of rectangles, where each rectangle can contain sub-rectangles forming a two-dimensional array.

## Level 0 (L0): Page-level structure
The topmost level representing the entire page divided into main sections:

- L0[0]: Header area
- L0[1]: Quote area  
- L0[2]: Cornell note area
- L0[3]: Footer area

## Level 1 (L1): First-level subdivisions

### L0[0] - Header Area
Subdivided into fields arranged horizontally:

- L0[0].L1[0]: Date field
- L0[0].L1[1]: Weather field
- L0[0].L1[2]: Review marker field

### L0[1] - Quote Area
Contains only one element:

- L0[1].L1[0]: Daily quote text

### L0[2] - Cornell Note Area
Subdivided vertically into three main parts:

- L0[2].L1[0]: Title section
- L0[2].L1[1]: Main content section
  - L0[2].L1[1].L2[0]: Keywords section
  - L0[2].L1[1].L2[1]: Notes section
- L0[2].L1[2]: Summary section

### L0[3] - Footer Area
Subdivided into spaced elements:

- L0[3].L1[0]: 2nd day review box
- L0[3].L1[1]: 7th day review box
- L0[3].L1[2]: 15th day review box
- L0[3].L1[3]: 28th day review box
- L0[3].L1[4]: 49th day review box
- L0[3].L1[5]: 83rd day review box

## Level 2 (L2): Second-level subdivisions

### L0[2].L1[1] - Main Content Section
Further divided horizontally into two parts:

- L0[2].L1[1].L2[0]: Keywords column (left side)
- L0[2].L1[1].L2[1]: Notes body (right side)

## Configuration Parameters

Each rectangular area can have its own set of configurable parameters:

- `height`: The height of the rectangular area
- `width`: The width of the rectangular area (can be absolute or relative)
- `label`: Text label associated with the area
- `text_alignment`: Horizontal text alignment (left, center, right)
- `text_padding`: Padding around text within the area
- `vertical_alignment`: Vertical text alignment (top, middle, bottom)
- `vertical_padding`: Vertical padding around text
- `spacing`: Spacing between elements in a group
- `width_ratio`: Width ratio for dividing horizontal sections (e.g., 0.3 for 30%)
- `line_count`: Number of lines for grid-based areas (used with grid line types)
- `border_enabled`: Whether to draw the border of the area (default: true)
- `text_position`: Relative position of text within its box (top-left, top-center, top-right, middle-left, center, middle-right, bottom-left, bottom-center, bottom-right)
- Additional style parameters depending on the area type

## Grid Line Types

Different areas can support various grid line styles:

- `blank`: Blank area with no grid lines
- `dotted`: Dotted grid pattern
- `four_line_three_grid`: Four-line three-grid pattern (commonly used for Chinese pinyin)
- `english_grid`: Three-line grid pattern for English writing practice
- `tianzige`: Traditional Chinese character practice grid (square with cross lines)
- `single_line`: Single horizontal lines for regular note-taking

## Grid Line Configuration Parameters

For grid-based areas (`four_line_three_grid`, `english_grid`, `tianzige`), the following configuration parameters can be specified:

- `grid_line_spacing`: Distance between grid lines (default varies by grid type)
- `grid_cell_size`: Size of each grid cell (applies to tianzige)
- `grid_line_style`: Style of lines (solid, dashed, dotted)
- `grid_line_color`: Color of the grid lines
- `grid_secondary_line_color`: Color of secondary/supporting lines (e.g., middle lines)
- `grid_offset_x`: Horizontal offset from the area border
- `grid_offset_y`: Vertical offset from the area border

## Dynamic Sizing

Areas and fields must automatically adjust their dimensions when the contained text exceeds the available space. The sizing behavior should follow these rules:

1. If text width exceeds the configured width, the area should expand horizontally to accommodate the text
2. If text height exceeds the configured height, the area should expand vertically to accommodate the text
3. Minimum dimensions should be maintained even when text is smaller than the configured size
4. When expanding dimensions, padding and margins should be preserved

## Software Implementation Considerations

To facilitate easier software implementation, the following structure should be followed:

### Component Hierarchy
1. **Page** - Top level container
   - **Header** - Contains metadata fields
   - **QuoteArea** - Inspirational quote section
   - **CornellModule** - Main note-taking area
     - **TitleSection** - Topic title
     - **ContentSection** - Main content area
       - **KeywordsSection** - Cue column
       - **NotesSection** - Notes column
     - **SummarySection** - Summary area
   - **Footer** - Review tracking section

### Configuration Approach
Each component should have its own configuration section in the JSON file with clearly defined properties. This allows for modular development and easier maintenance.