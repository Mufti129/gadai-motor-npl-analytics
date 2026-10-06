"""
Plot Styling & Design System.
Defines publication-grade typography, color palettes, and layout standards.
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Color Palette Definitions
PRIMARY_BLUE = "#1f77b4"
DANGER_RED = "#d9534f"
SUCCESS_GREEN = "#2ca02c"
WARNING_ORANGE = "#ff7f0e"
NEUTRAL_GRAY = "#7f8c8d"
LIGHT_BG = "#f8f9fa"

PALETTE_NPL = {
    0: "#2b5c8f",  # Lancar (Professional Deep Blue)
    1: "#c0392b"   # Macet / NPL (Warning Crimson)
}

PALETTE_CATEGORIES = [
    "#2b5c8f", "#e67e22", "#27ae60", "#8e44ad",
    "#d35400", "#16a085", "#2980b9", "#c0392b"
]


def set_publication_style():
    """
    Configure clean, modern aesthetics for Matplotlib and Seaborn figures.
    """
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial", "Lucida Grande"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "semibold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 15,
        "figure.titleweight": "bold",
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.edgecolor": "#bdc3c7",
        "axes.linewidth": 0.8,
        "grid.color": "#ecf0f1",
        "grid.linestyle": "--",
        "grid.alpha": 0.7
    })
