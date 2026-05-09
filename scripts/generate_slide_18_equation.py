"""
Generates the EMAILS + JIRA CSV = MASTER DATASET data-flow visual for slide 18.
Outputs both an editable SVG and a 1600x500 transparent PNG to the project root.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ---- canvas ----
W, H = 1600, 500
DPI = 100

# ---- card geometry ----
CARD_W, CARD_H = 380, 280
CARD_Y = 88
CENTER_Y = CARD_Y + CARD_H / 2  # 228

CARDS = [
    {
        "x": 150,
        "header": "EMAILS",
        "body": ["46,486 rows", "behavior_score", "mailing lists"],
        "caption": "Email-level sentiment",
        "fill": "#E6F1FB", "border": "#185FA5", "text": "#0C447C",
        "border_w": 1.5,
    },
    {
        "x": 610,
        "header": "JIRA CSV",
        "body": ["~60K rows", "key, status,", "priority, summary"],
        "caption": "Ticket-level metadata",
        "fill": "#FAEEDA", "border": "#BA7517", "text": "#633806",
        "border_w": 1.5,
    },
    {
        "x": 1070,
        "header": "MASTER DATASET",
        "body": ["916 unique tickets", "communication +", "structural metadata"],
        "caption": "Joined on ticket_key",
        "fill": "#E1F5EE", "border": "#0F6E56", "text": "#085041",
        "border_w": 2.5,
    },
]

OPERATORS = [(570, "+"), (1030, "=")]

# Use a monospace family chain — JetBrains Mono if installed, else fallback
plt.rcParams["font.family"] = ["JetBrains Mono", "DejaVu Sans Mono", "monospace"]

fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)  # invert y so coordinates count from the top
ax.axis("off")

for card in CARDS:
    rect = FancyBboxPatch(
        (card["x"], CARD_Y), CARD_W, CARD_H,
        boxstyle="round,pad=0,rounding_size=12",
        facecolor=card["fill"],
        edgecolor=card["border"],
        linewidth=card["border_w"],
    )
    ax.add_patch(rect)

    cx = card["x"] + CARD_W / 2

    # Header
    ax.text(cx, CARD_Y + 77, card["header"],
            ha="center", va="center",
            fontsize=28, fontweight=500, color=card["text"])

    # 3 body lines, evenly spaced
    body_y0 = CARD_Y + 142
    for i, line in enumerate(card["body"]):
        ax.text(cx, body_y0 + i * 35, line,
                ha="center", va="center",
                fontsize=20, color=card["text"])

    # Caption 20px beneath the card
    ax.text(cx, CARD_Y + CARD_H + 28, card["caption"],
            ha="center", va="center",
            fontsize=16, fontstyle="italic", color="#5F5E5A")

# Operators
for x, sym in OPERATORS:
    ax.text(x, CENTER_Y, sym,
            ha="center", va="center",
            fontsize=80, fontweight="bold", color="#444441")

# Save both formats
svg_path = "slide_18_equation.svg"
png_path = "slide_18_equation.png"
fig.savefig(svg_path, transparent=True, bbox_inches=None)
fig.savefig(png_path, transparent=True, dpi=DPI, bbox_inches=None)
plt.close(fig)

print(f"Saved: {svg_path}")
print(f"Saved: {png_path}")
