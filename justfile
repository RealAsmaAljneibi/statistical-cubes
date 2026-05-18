# Statistical Cube Builder – task runner
# Install: https://github.com/casey/just

# Show available recipes
default:
    @just --list

# Install all Python dependencies
install:
    uv sync

# Run the notebook in view-only mode (hides code)1
run:
    marimo run cube_builder.py

# Open the notebook in edit mode (shows and allows changing cells)
edit:
    marimo edit cube_builder.py

# Regenerate the synthetic employee register dataset
data:
    python scripts/generate_data.py

# Export to a self-contained WASM HTML file (for GitHub Pages)
export:
    marimo export html-wasm cube_builder.py -o public/index.html --mode run

# Install deps, regenerate data, then run
dev: install data run

# Open the paper's notebook in interactive app mode (hides code, reader-facing)
open:
    marimo run ../cube_builder.py

# Open the paper's notebook in edit mode (shows cells, for development)
edit-paper:
    marimo edit ../cube_builder.py
