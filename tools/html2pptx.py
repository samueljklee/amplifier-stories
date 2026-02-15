#!/usr/bin/env python3
"""
html2pptx.py - Convert Amplifier Stories HTML decks to PowerPoint presentations.

This tool parses HTML presentation decks created with the Amplifier Stories style
and generates equivalent PowerPoint presentations using python-pptx.

Usage:
    uv run --with python-pptx,beautifulsoup4,lxml python tools/html2pptx.py <input.html> [output.pptx]

If output path is not specified, uses the input filename with .pptx extension.

Supports all Amplifier Stories element types including:
- Slide structure (div.slide and section.slide)
- Headlines, subheads, section labels
- Cards in grid layouts (thirds, halves, fourths, grid-2 through grid-5)
- Code blocks with syntax highlighting
- Flow diagrams and architecture diagrams
- Stats grids and stat rows
- Tenet boxes, highlight boxes
- Feature lists, tables, versus comparisons
- Notification stacks
- Comparison tables
- CSS variable extraction for per-deck theming
"""

import argparse
import re
import sys
import warnings
from copy import deepcopy
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, Tag
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# ── Slide dimensions ──────────────────────────────────────────────────────────
SLIDE_WIDTH = 10.0  # inches
SLIDE_HEIGHT = 5.625  # inches (16:9)
CONTENT_LEFT = 0.8
CONTENT_WIDTH = 8.4
CONTENT_RIGHT = CONTENT_LEFT + CONTENT_WIDTH

# ── Spacing constants (consistent gap system) ────────────────────────────────
GAP_TIGHT = 0.08  # within a card, between tightly related elements
GAP_NORMAL = 0.10  # standard gap between elements on a slide
GAP_SECTION = 0.20  # gap between major sections (e.g., headline to cards)

# ── Color palette (matching Amplifier Stories dark-mode style) ────────────────
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MS_BLUE = RGBColor(0x00, 0x78, 0xD4)
MS_CYAN = RGBColor(0x50, 0xE6, 0xFF)
MS_GREEN = RGBColor(0x00, 0xCC, 0x6A)
MS_ORANGE = RGBColor(0xFF, 0x9F, 0x0A)
MS_RED = RGBColor(0xFF, 0x45, 0x3A)
MS_PURPLE = RGBColor(0x8B, 0x5C, 0xF6)
GRAY_70 = RGBColor(0xB3, 0xB3, 0xB3)
GRAY_50 = RGBColor(0x80, 0x80, 0x80)
DARK_GRAY = RGBColor(0x1A, 0x1A, 0x1A)
BORDER_GRAY = RGBColor(0x33, 0x33, 0x33)
CODE_BG = RGBColor(0x0D, 0x11, 0x17)

# Code syntax colors
CODE_GREEN = RGBColor(0x4A, 0xDE, 0x80)
CODE_BLUE = RGBColor(0x60, 0xA5, 0xFA)
CODE_YELLOW = RGBColor(0xFB, 0xBF, 0x24)
CODE_GRAY = RGBColor(0x6B, 0x73, 0x80)
CODE_PURPLE = RGBColor(0xC0, 0x84, 0xFC)
CODE_STRING = RGBColor(0xFB, 0xBF, 0x24)
CODE_DEFAULT = RGBColor(0xE6, 0xE6, 0xE6)

# ── Default font ──────────────────────────────────────────────────────────────
DEFAULT_FONT = "Arial"
CODE_FONT = "Consolas"


# ── Helper: hex string → RGBColor ────────────────────────────────────────────
def hex_to_rgb(hex_str: str) -> Optional[RGBColor]:
    """Convert #RGB or #RRGGBB to RGBColor."""
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        return None
    try:
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return RGBColor(r, g, b)
    except ValueError:
        return None


def parse_color_from_class(classes: list[str]) -> Optional[RGBColor]:
    """Extract accent color from CSS classes."""
    color_map = {
        "green": MS_GREEN,
        "orange": MS_ORANGE,
        "red": MS_RED,
        "ms-green": MS_GREEN,
        "ms-orange": MS_ORANGE,
        "ms-red": MS_RED,
        "ms-blue": MS_BLUE,
        "ms-cyan": MS_CYAN,
        "ms-purple": MS_PURPLE,
        "warning": MS_ORANGE,
    }
    for cls in classes:
        if cls in color_map:
            return color_map[cls]
    return None


def _replace_br_tags(element: Tag):
    """Replace all <br> tags with newline characters BEFORE text extraction."""
    for br in element.find_all("br"):
        br.replace_with("\n")


def get_text(element: Optional[Tag]) -> str:
    """Extract text content from an element, handling None and <br> tags."""
    if element is None:
        return ""
    # Work on a copy so we don't mutate the original soup
    el_copy = deepcopy(element)
    _replace_br_tags(el_copy)
    text = el_copy.get_text()
    # Collapse runs of spaces (but keep newlines)
    lines = text.split("\n")
    lines = [" ".join(line.split()) for line in lines]
    return "\n".join(lines).strip()


def get_rich_text(element: Optional[Tag]) -> list[dict]:
    """Extract rich text runs preserving bold/italic/highlight spans.

    Returns a list of dicts: [{"text": str, "bold": bool, "italic": bool, "color": RGBColor|None}]
    """
    if element is None:
        return []

    el_copy = deepcopy(element)
    _replace_br_tags(el_copy)
    runs: list[dict] = []

    for child in el_copy.descendants:
        if isinstance(child, NavigableString):
            text = str(child)
            if not text:
                continue
            # Collapse HTML indentation whitespace (keep \n from <br> tags)
            lines = text.split("\n")
            lines = [" ".join(line.split()) for line in lines]
            text = "\n".join(lines)
            if not text or text.isspace():
                continue
            # Determine formatting from parent chain
            bold = False
            italic = False
            color = None
            parent = child.parent
            while parent and parent.name:
                if parent.name in ("strong", "b"):
                    bold = True
                if parent.name in ("em", "i"):
                    italic = True
                if parent.name == "span":
                    cls = parent.get("class", [])
                    if "highlight" in cls:
                        color = MS_CYAN
                    elif "check" in cls:
                        color = MS_GREEN
                parent = parent.parent
            runs.append({"text": text, "bold": bold, "italic": italic, "color": color})

    # Merge adjacent runs with identical formatting
    merged: list[dict] = []
    for run in runs:
        if (
            merged
            and merged[-1]["bold"] == run["bold"]
            and merged[-1]["italic"] == run["italic"]
            and merged[-1]["color"] == run["color"]
        ):
            merged[-1]["text"] += run["text"]
        else:
            merged.append(run)

    # Strip leading whitespace from first run, trailing from last
    if merged:
        merged[0]["text"] = merged[0]["text"].lstrip()
        merged[-1]["text"] = merged[-1]["text"].rstrip()
        # Remove empty runs
        merged = [r for r in merged if r["text"]]

    return merged


# ── Low-level shape helpers ───────────────────────────────────────────────────


def set_slide_background(slide, color=BLACK):
    """Set solid background color for a slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _set_font(
    run,
    name: str = DEFAULT_FONT,
    size: int = 14,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = WHITE,
):
    """Apply font properties to a text run."""
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def add_text_box(
    slide,
    text: str,
    left: float,
    top: float,
    width: float,
    height: float,
    font_size: int = 14,
    font_name: str = DEFAULT_FONT,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = WHITE,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    wrap: bool = True,
    vertical_anchor: MSO_ANCHOR = MSO_ANCHOR.TOP,
):
    """Add a text box with specified styling. Every run gets explicit font name."""
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    tf.vertical_anchor = vertical_anchor

    # Handle multi-line text
    lines = text.split("\n")
    for line_idx, line in enumerate(lines):
        if line_idx == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        _set_font(
            run, name=font_name, size=font_size, bold=bold, italic=italic, color=color
        )

    return box


def add_rich_text_box(
    slide,
    runs: list[dict],
    left: float,
    top: float,
    width: float,
    height: float,
    font_size: int = 14,
    font_name: str = DEFAULT_FONT,
    default_color: RGBColor = WHITE,
    align: PP_ALIGN = PP_ALIGN.LEFT,
):
    """Add a text box with multiple formatting runs."""
    box = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = box.text_frame
    tf.word_wrap = True

    # Split runs by newlines into paragraphs
    paragraphs: list[list[dict]] = [[]]
    for r in runs:
        parts = r["text"].split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                paragraphs.append([])
            if part:
                paragraphs[-1].append({**r, "text": part})

    for p_idx, p_runs in enumerate(paragraphs):
        if p_idx == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        if not p_runs:
            # Empty paragraph (blank line)
            run = p.add_run()
            run.text = ""
            _set_font(run, name=font_name, size=font_size, color=default_color)
        else:
            for r in p_runs:
                run = p.add_run()
                run.text = r["text"]
                _set_font(
                    run,
                    name=font_name,
                    size=font_size,
                    bold=r.get("bold", False),
                    italic=r.get("italic", False),
                    color=r.get("color") or default_color,
                )

    return box


def add_filled_box(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    fill_color: RGBColor = DARK_GRAY,
    border_color: Optional[RGBColor] = BORDER_GRAY,
    border_width: float = 1.0,
    shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
):
    """Add a filled shape (card background, code block bg, etc.)."""
    shape = slide.shapes.add_shape(
        shape_type, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()
    return shape


# ── Element-level helpers ─────────────────────────────────────────────────────


def _estimate_text_height(
    text: str, font_size_pt: int, box_width_inches: float, line_spacing: float = 1.2
) -> float:
    """Estimate rendered text height based on character count and box width.

    Uses a rough heuristic for proportional fonts to determine how many lines
    the text will wrap to, then computes the total height including padding.
    """
    chars_per_inch = 72 / font_size_pt * 1.8  # rough heuristic
    chars_per_line = int(box_width_inches * chars_per_inch)
    if chars_per_line < 1:
        chars_per_line = 1
    num_lines = max(1, -(-len(text) // chars_per_line))  # ceil division
    line_height = font_size_pt / 72 * line_spacing
    return num_lines * line_height + 0.1  # 0.1" padding


def add_section_label(slide, text: str, top: float = 0.6, color: RGBColor = MS_BLUE):
    """Add a colored uppercase section label."""
    return add_text_box(
        slide,
        text.upper(),
        left=CONTENT_LEFT,
        top=top,
        width=CONTENT_WIDTH,
        height=0.4,
        font_size=14,
        bold=True,
        color=color,
        wrap=False,
    )


def add_headline(
    slide,
    text: str,
    top: float = 1.1,
    size: int = 48,
    center: bool = False,
    color: RGBColor = WHITE,
):
    """Add a large headline with dynamically estimated box height."""
    # Estimate actual height needed based on text length and font size
    box_height = _estimate_text_height(text, size, CONTENT_WIDTH)
    # Apply sensible min/max: at least one line, at most 2.0"
    min_height = size / 72 * 1.2 + 0.1  # single line minimum
    box_height = max(min_height, min(box_height, 2.0))
    return add_text_box(
        slide,
        text,
        left=CONTENT_LEFT,
        top=top,
        width=CONTENT_WIDTH,
        height=box_height,
        font_size=size,
        bold=True,
        color=color,
        align=PP_ALIGN.CENTER if center else PP_ALIGN.LEFT,
    )


def add_subhead(
    slide, text: str, top: float = 2.8, color: RGBColor = GRAY_70, center: bool = False
):
    """Add a subtitle/subheading with dynamically estimated box height."""
    # Estimate height needed instead of fixed 1.0"
    box_height = _estimate_text_height(text, 24, CONTENT_WIDTH)
    box_height = max(0.5, min(box_height, 1.5))
    return add_text_box(
        slide,
        text,
        left=CONTENT_LEFT,
        top=top,
        width=CONTENT_WIDTH,
        height=box_height,
        font_size=24,
        color=color,
        align=PP_ALIGN.CENTER if center else PP_ALIGN.LEFT,
    )


def add_card(
    slide,
    title: str,
    text: str,
    left: float,
    top: float,
    width: float = 2.6,
    height: float = 1.8,
    title_color: RGBColor = MS_BLUE,
    rich_runs: Optional[list[dict]] = None,
):
    """Add a card with title and description."""
    # Card background
    add_filled_box(slide, left, top, width, height)

    # Adaptive title height: scale with card height, estimate from text
    title_height = min(0.4, height * 0.25)
    title_est = _estimate_text_height(title, 16, width - 0.3)
    title_height = max(title_height, min(title_est, 0.5))

    # Card title
    add_text_box(
        slide,
        title,
        left=left + 0.15,
        top=top + 0.15,
        width=width - 0.3,
        height=title_height,
        font_size=16,
        bold=True,
        color=title_color,
    )

    # Card text (rich or plain)
    text_top = top + 0.15 + title_height + GAP_TIGHT  # title_top + title_height + gap
    text_height = height - (
        0.15 + title_height + GAP_TIGHT + 0.05
    )  # pad + title + gap + bottom_pad
    if rich_runs:
        add_rich_text_box(
            slide,
            rich_runs,
            left=left + 0.15,
            top=text_top,
            width=width - 0.3,
            height=max(text_height, 0.2),
            font_size=12,
            default_color=GRAY_70,
        )
    else:
        add_text_box(
            slide,
            text,
            left=left + 0.15,
            top=text_top,
            width=width - 0.3,
            height=max(text_height, 0.2),
            font_size=12,
            color=GRAY_70,
        )


def add_tenet(
    slide,
    title: str,
    text: str,
    left: float,
    top: float,
    width: float = 4.0,
    height: float = 0.9,
    accent_color: RGBColor = MS_GREEN,
):
    """Add a tenet box with left border accent."""
    bg_map = {
        MS_GREEN: RGBColor(0x0D, 0x1A, 0x0D),
        MS_ORANGE: RGBColor(0x1A, 0x15, 0x0D),
        MS_RED: RGBColor(0x1A, 0x0D, 0x0D),
    }
    bg_color = bg_map.get(accent_color, RGBColor(0x0D, 0x15, 0x1A))

    # Background
    add_filled_box(
        slide, left, top, width, height, fill_color=bg_color, border_color=None
    )

    # Left accent bar
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.05), Inches(height)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent_color
    bar.line.fill.background()

    # Title
    add_text_box(
        slide,
        title,
        left=left + 0.15,
        top=top + 0.1,
        width=width - 0.3,
        height=0.3,
        font_size=14,
        bold=True,
        color=WHITE,
    )

    # Text
    add_text_box(
        slide,
        text,
        left=left + 0.15,
        top=top + 0.4,
        width=width - 0.3,
        height=height - 0.5,
        font_size=11,
        color=GRAY_70,
    )


def add_highlight_box(
    slide,
    text: str,
    top: float = 4.2,
    color: RGBColor = MS_BLUE,
    rich_runs: Optional[list[dict]] = None,
):
    """Add a highlight/callout box."""
    bg_map = {
        MS_GREEN: RGBColor(0x00, 0x1A, 0x0D),
        MS_ORANGE: RGBColor(0x33, 0x1A, 0x00),
        MS_RED: RGBColor(0x1A, 0x0D, 0x0D),
    }
    bg_color = bg_map.get(color, RGBColor(0x00, 0x1A, 0x33))

    add_filled_box(
        slide,
        CONTENT_LEFT,
        top,
        CONTENT_WIDTH,
        0.7,
        fill_color=bg_color,
        border_color=color,
        border_width=1,
    )

    if rich_runs:
        add_rich_text_box(
            slide,
            rich_runs,
            left=CONTENT_LEFT + 0.2,
            top=top + 0.12,
            width=CONTENT_WIDTH - 0.4,
            height=0.5,
            font_size=14,
            default_color=WHITE,
        )
    else:
        add_text_box(
            slide,
            text,
            left=CONTENT_LEFT + 0.2,
            top=top + 0.12,
            width=CONTENT_WIDTH - 0.4,
            height=0.5,
            font_size=14,
            color=WHITE,
        )


# ── CSS variable extraction ──────────────────────────────────────────────────


def extract_css_vars(soup: BeautifulSoup) -> dict[str, str]:
    """Extract CSS custom properties from <style> blocks."""
    result: dict[str, str] = {}
    for style_tag in soup.find_all("style"):
        css_text = style_tag.string or ""
        # Match --variable-name: value patterns
        for m in re.finditer(r"--([\w-]+)\s*:\s*([^;]+)", css_text):
            name = m.group(1).strip()
            value = m.group(2).strip()
            result[name] = value
    return result


def resolve_accent_color(css_vars: dict[str, str]) -> RGBColor:
    """Determine the accent color for the deck from CSS variables."""
    # Try common variable names
    for var_name in ("color-accent", "accent"):
        val = css_vars.get(var_name, "")
        if val.startswith("#"):
            rgb = hex_to_rgb(val)
            if rgb:
                return rgb
    return MS_BLUE


# ── Main converter class ─────────────────────────────────────────────────────


class HTMLToPPTXConverter:
    """Converts Amplifier Stories HTML decks to PowerPoint."""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "lxml")
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_WIDTH)
        self.prs.slide_height = Inches(SLIDE_HEIGHT)
        self.blank_layout = self.prs.slide_layouts[6]

        # Extract per-deck theming from CSS variables
        self.css_vars = extract_css_vars(self.soup)
        self.accent_color = resolve_accent_color(self.css_vars)

        # Track warnings
        self.warnings: list[str] = []

    # ── Slide extraction ─────────────────────────────────────────────────────

    def extract_slides(self) -> list[Tag]:
        """Extract all slide elements (div.slide AND section.slide)."""
        return self.soup.find_all(["div", "section"], class_="slide")

    def is_centered(self, slide_div: Tag) -> bool:
        """Check if slide has center class."""
        classes = slide_div.get("class", [])
        return "center" in classes

    # ── Main slide processor ─────────────────────────────────────────────────

    def process_slide(self, slide_div: Tag, slide_num: int):
        """Process a single slide and add to presentation."""
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide)

        is_centered = self.is_centered(slide_div)
        current_top = 0.6

        # Track which child elements we've handled (to avoid double-processing)
        handled_elements: set[int] = set()

        # ── Section number + section title (alternative to section-label) ──
        section_number = slide_div.find(class_="section-number")
        if section_number:
            add_section_label(
                slide,
                get_text(section_number),
                top=current_top,
                color=self.accent_color,
            )
            current_top += 0.4 + GAP_TIGHT  # section-label height + tight gap
            handled_elements.add(id(section_number))

        section_title = slide_div.find(class_="section-title")
        if section_title:
            add_text_box(
                slide,
                get_text(section_title),
                left=CONTENT_LEFT,
                top=current_top,
                width=CONTENT_WIDTH,
                height=0.5,
                font_size=20,
                bold=True,
                color=WHITE,
            )
            current_top += 0.5 + GAP_NORMAL
            handled_elements.add(id(section_title))

        # ── Section label ────────────────────────────────────────────────────
        section_label = slide_div.find(class_="section-label")
        if section_label:
            if is_centered:
                current_top = 1.0
            add_section_label(
                slide, get_text(section_label), top=current_top, color=self.accent_color
            )
            current_top += 0.4 + GAP_NORMAL  # section-label height + normal gap
            handled_elements.add(id(section_label))

        # ── Headline (h1 or h2.headline) ─────────────────────────────────────
        headline = slide_div.find(["h1", "h2"], class_="headline") or slide_div.find(
            "h1"
        )
        if headline:
            text = get_text(headline)
            has_gradient = "big-text" in headline.get("class", [])
            color = MS_CYAN if has_gradient else WHITE
            size = 56 if headline.name == "h1" or has_gradient else 40

            if is_centered:
                current_top = max(current_top, 1.5)

            add_headline(
                slide, text, top=current_top, size=size, center=is_centered, color=color
            )
            # Advance by dynamically estimated headline height + section gap
            headline_height = _estimate_text_height(text, size, CONTENT_WIDTH)
            min_h = size / 72 * 1.2 + 0.1
            headline_height = max(min_h, min(headline_height, 2.0))
            current_top += headline_height + GAP_SECTION
            handled_elements.add(id(headline))

        # ── Medium headline ──────────────────────────────────────────────────
        medium_headline = slide_div.find(class_="medium-headline")
        if medium_headline and id(medium_headline) not in handled_elements:
            mh_text = get_text(medium_headline)
            add_headline(
                slide,
                mh_text,
                top=current_top,
                size=36,
                center=is_centered,
            )
            mh_height = _estimate_text_height(mh_text, 36, CONTENT_WIDTH)
            mh_height = max(36 / 72 * 1.2 + 0.1, min(mh_height, 2.0))
            current_top += mh_height + GAP_SECTION
            handled_elements.add(id(medium_headline))

        # ── Subhead ──────────────────────────────────────────────────────────
        subhead = slide_div.find(class_="subhead")
        if subhead:
            text = get_text(subhead)
            add_subhead(slide, text, top=current_top, center=is_centered)
            # Advance by the same box height that add_subhead() computed + gap
            sub_height = _estimate_text_height(text, 24, CONTENT_WIDTH)
            sub_height = max(0.5, min(sub_height, 1.5))  # must match add_subhead caps
            current_top += sub_height + GAP_NORMAL
            handled_elements.add(id(subhead))

        # ── Architecture diagram (preformatted text art) ─────────────────────
        arch_diagram = slide_div.find(class_="architecture-diagram")
        if arch_diagram:
            self._add_architecture_diagram(slide, arch_diagram, current_top)
            current_top += 3.0
            handled_elements.add(id(arch_diagram))

        # ── Comparison table (grid layout) ───────────────────────────────────
        comp_table = slide_div.find(class_="comparison-table")
        if comp_table:
            self._add_comparison_table(slide, comp_table, current_top)
            current_top += 2.2
            handled_elements.add(id(comp_table))

        # ── Cards in grid containers ─────────────────────────────────────────
        grid_classes = [
            "thirds",
            "halves",
            "fourths",
            "grid",
            "grid-2",
            "grid-3",
            "grid-4",
            "grid-5",
        ]
        card_containers = slide_div.find_all(
            class_=lambda c: c and any(gc in c for gc in grid_classes)
        )
        for container in card_containers:
            if id(container) in handled_elements:
                continue

            # Find cards or module-cards inside
            cards = container.find_all(class_=["card", "module-card"], recursive=False)
            if not cards:
                # Try deeper (some decks nest differently)
                cards = container.find_all(class_=["card", "module-card"])

            if cards:
                cards_height = self._add_cards(slide, cards, current_top, container)
                current_top += cards_height + GAP_SECTION
                handled_elements.add(id(container))
                for c in cards:
                    handled_elements.add(id(c))

        # ── Standalone cards not in containers ───────────────────────────────
        standalone_cards = [
            c
            for c in slide_div.find_all(class_=["card", "module-card"])
            if id(c) not in handled_elements
            and not c.find_parent(
                class_=lambda x: x and any(gc in x for gc in grid_classes)
            )
        ]
        if standalone_cards:
            cards_height = self._add_cards(slide, standalone_cards, current_top)
            current_top += cards_height + GAP_SECTION
            for c in standalone_cards:
                handled_elements.add(id(c))

        # ── Principle boxes (numbered principles in grid layouts) ─────────
        principles = [
            p
            for p in slide_div.find_all(class_="principle")
            if id(p) not in handled_elements
        ]
        if principles:
            self._add_principles(slide, principles, current_top)
            num_rows = -(-len(principles) // 2)  # ceil division
            row_height = 0.85
            row_gap = 0.1
            current_top += num_rows * (row_height + row_gap)
            for p in principles:
                handled_elements.add(id(p))

        # ── Code blocks ──────────────────────────────────────────────────────
        code_blocks = slide_div.find_all(class_="code-block")
        for cb in code_blocks:
            if id(cb) in handled_elements:
                continue
            self._add_code_block(slide, cb, current_top)
            # Estimate height from line count
            lines = get_text(cb).count("\n") + 1
            current_top += max(1.2, min(lines * 0.18 + 0.4, 3.5))
            handled_elements.add(id(cb))

        # ── Flow diagrams ────────────────────────────────────────────────────
        flow_diagrams = slide_div.find_all(class_=["flow-diagram", "workflow"])
        for fd in flow_diagrams:
            if id(fd) in handled_elements:
                continue
            self._add_flow_diagram(slide, fd, current_top)
            current_top += 1.2
            handled_elements.add(id(fd))

        # ── Tenet boxes ──────────────────────────────────────────────────────
        tenets = slide_div.find_all(class_="tenet")
        if tenets:
            self._add_tenets(slide, tenets, current_top)
            current_top += len(tenets) * 0.5 + 0.5

        # ── Versus comparison ────────────────────────────────────────────────
        versus = slide_div.find(class_="versus")
        if versus:
            self._add_versus(slide, versus, current_top)
            current_top += 2.5

        # ── Tables (data-table or plain table) ───────────────────────────────
        tables = slide_div.find_all("table")
        for table in tables:
            if id(table) in handled_elements:
                continue
            self._add_table(slide, table, current_top)
            rows = table.find_all("tr")
            current_top += len(rows) * 0.32 + 0.3
            handled_elements.add(id(table))

        # ── Feature lists ────────────────────────────────────────────────────
        feature_lists = slide_div.find_all(class_="feature-list")
        for fl in feature_lists:
            if fl.find_parent(class_="versus"):
                continue
            self._add_feature_list(slide, fl, current_top)
            items = fl.find_all("li")
            current_top += len(items) * 0.35 + GAP_SECTION

        # ── Notification stacks ──────────────────────────────────────────────
        notif_stack = slide_div.find(class_="notification-stack")
        if notif_stack and id(notif_stack) not in handled_elements:
            self._add_notification_stack(slide, notif_stack, current_top)
            current_top += 2.5
            handled_elements.add(id(notif_stack))

        # ── Stats grid / stat row ────────────────────────────────────────────
        stat_container = slide_div.find(class_="stat-grid") or slide_div.find(
            class_="stat-row"
        )
        if stat_container and id(stat_container) not in handled_elements:
            self._add_stats(slide, stat_container, current_top)
            current_top += 1.2
            handled_elements.add(id(stat_container))

        # ── Highlight boxes ──────────────────────────────────────────────────
        highlight_boxes = slide_div.find_all(class_="highlight-box")
        for hb in highlight_boxes:
            if id(hb) in handled_elements:
                continue
            classes = hb.get("class", [])
            color = parse_color_from_class(classes) or self.accent_color
            rich = get_rich_text(hb)
            plain = get_text(hb)
            add_highlight_box(
                slide,
                plain,
                top=min(current_top, 4.5),
                color=color,
                rich_runs=rich if len(rich) > 1 else None,
            )
            current_top += 0.8
            handled_elements.add(id(hb))

        # ── Quote ────────────────────────────────────────────────────────────
        quote = slide_div.find(class_="quote")
        if quote:
            self._add_quote(slide, quote, current_top)
            current_top += 1.5  # quote height (1.2) + attribution (0.3)
            handled_elements.add(id(quote))

        # ── Small text (footer) ──────────────────────────────────────────────
        small_texts = slide_div.find_all(class_="small-text")
        small_text_top = max(current_top, 4.8)
        for st in small_texts:
            if id(st) in handled_elements:
                continue
            add_text_box(
                slide,
                get_text(st),
                left=CONTENT_LEFT,
                top=small_text_top,
                width=CONTENT_WIDTH,
                height=0.4,
                font_size=14,
                color=GRAY_50,
                align=PP_ALIGN.CENTER if is_centered else PP_ALIGN.LEFT,
            )
            small_text_top += 0.4
            handled_elements.add(id(st))
        current_top = small_text_top

        # ── Fallback: render unrecognized elements with text content ─────────
        # Instead of silently dropping unknown elements, render them as
        # generic text boxes so no content vanishes.
        for el in slide_div.children:
            if not isinstance(el, Tag):
                continue
            if id(el) in handled_elements:
                continue
            # Skip elements that are parents of already-handled children
            if any(
                id(desc) in handled_elements
                for desc in el.descendants
                if isinstance(desc, Tag)
            ):
                continue
            if hasattr(el, "get_text") and el.get_text(strip=True):
                text = get_text(el)
                if text and len(text) > 5:  # skip trivial fragments
                    fb_height = min(1.0, len(text) / 80 * 0.3 + 0.3)
                    add_text_box(
                        slide,
                        text,
                        left=CONTENT_LEFT,
                        top=current_top,
                        width=CONTENT_WIDTH,
                        height=fb_height,
                        font_size=14,
                        color=GRAY_70,
                    )
                    current_top += fb_height + GAP_NORMAL
                    handled_elements.add(id(el))

        # ── Overflow warning ─────────────────────────────────────────────────
        if current_top > SLIDE_HEIGHT + 0.5:
            self.warnings.append(
                f'Slide {slide_num}: content extends to {current_top:.1f}" '
                f'(slide height is {SLIDE_HEIGHT}")'
            )

    # ── Card layouts ─────────────────────────────────────────────────────────

    def _add_cards(
        self, slide, cards: list[Tag], top: float, container: Optional[Tag] = None
    ) -> float:
        """Add a row of cards to the slide. Returns total height consumed."""
        num_cards = len(cards)
        if num_cards == 0:
            return 0.0

        # Determine column count from container class.
        #
        # CSS auto-fit classes ("halves", "thirds") use:
        #   grid-template-columns: repeat(auto-fit, minmax(min(Npx, 100%), 1fr))
        # At presentation viewport (~1120px content), "halves" (min 300px) fits
        # up to 3 columns; "thirds" (min 280px) fits up to 3.  Explicit grid-N
        # classes always force exactly N columns.  For auto-fit classes we cap at
        # the CSS-implied maximum and let card count fill rows naturally.
        forced_cols = None
        if container:
            cls = " ".join(container.get("class", []))
            if "grid-5" in cls or "fifths" in cls:
                forced_cols = 5
            elif "grid-4" in cls or "fourths" in cls:
                forced_cols = 4
            elif "grid-3" in cls or "thirds" in cls:
                forced_cols = 3
            elif "grid-2" in cls:
                forced_cols = 2
            elif "halves" in cls:
                # auto-fit with minmax(300px, 1fr) → up to 3 cols at 1120px
                forced_cols = min(num_cards, 3)

        cols = forced_cols or min(num_cards, 4)
        num_rows = -(-num_cards // cols)  # ceil division
        gap = 0.2
        total_width = CONTENT_WIDTH
        card_width = (total_width - gap * (cols - 1)) / cols
        start_left = CONTENT_LEFT

        # Adaptive card height: fit within remaining slide space
        available_height = SLIDE_HEIGHT - top - 0.3  # 0.3" bottom margin
        row_gap = 0.2  # gap between rows of cards
        if num_rows == 1:
            card_height = min(1.8, available_height)
        else:
            # Divide available space among rows with gaps between them
            card_height = min(
                1.8, (available_height - row_gap * (num_rows - 1)) / num_rows
            )
        card_height = max(card_height, 0.8)  # never smaller than 0.8"

        # Center cards if fewer than cols
        if num_cards < cols:
            actual_width = num_cards * card_width + (num_cards - 1) * gap
            start_left = CONTENT_LEFT + (total_width - actual_width) / 2

        for i, card_el in enumerate(cards):
            col = i % cols
            row = i // cols
            left = start_left + col * (card_width + gap)
            row_top = top + row * (card_height + row_gap)

            # Detect card type
            is_module_card = "module-card" in card_el.get("class", [])

            if is_module_card:
                self._add_module_card(
                    slide, card_el, left, row_top, card_width, card_height
                )
            else:
                title_el = card_el.find(class_="card-title")
                text_el = card_el.find(class_=["card-text", "card-desc"])
                number_el = card_el.find(class_="card-number")

                title = get_text(title_el) if title_el else ""
                text = get_text(text_el) if text_el else ""
                rich = get_rich_text(text_el) if text_el else []

                if number_el:
                    number = get_text(number_el)
                    self._add_number_card(
                        slide,
                        number,
                        title,
                        text,
                        left,
                        row_top,
                        card_width,
                        card_height,
                    )
                else:
                    add_card(
                        slide,
                        title,
                        text,
                        left,
                        row_top,
                        width=card_width,
                        height=card_height,
                        title_color=self.accent_color,
                        rich_runs=rich if len(rich) > 1 else None,
                    )

        # Return total height consumed by all rows
        return num_rows * card_height + (num_rows - 1) * row_gap

    def _add_principles(self, slide, principles: list[Tag], top: float):
        """Add numbered principle boxes in a two-column tenet layout."""
        cols = 2
        col_width = CONTENT_WIDTH / 2 - 0.1
        row_height = 0.85
        row_gap = 0.1

        for i, principle in enumerate(principles):
            col = i % cols
            row = i // cols
            left = CONTENT_LEFT + col * (col_width + 0.2)
            ptop = top + row * (row_height + row_gap)

            num_el = principle.find(class_="principle-number")
            content_el = principle.find(class_="principle-content")
            number = get_text(num_el) if num_el else str(i + 1)
            title = ""
            desc = ""
            if content_el:
                h3 = content_el.find("h3")
                p_tag = content_el.find("p")
                title = get_text(h3) if h3 else ""
                desc = get_text(p_tag) if p_tag else ""

            add_tenet(
                slide,
                f"{number}. {title}",
                desc,
                left,
                ptop,
                width=col_width,
                height=row_height,
                accent_color=self.accent_color,
            )

    def _add_module_card(
        self,
        slide,
        card_el: Tag,
        left: float,
        top: float,
        width: float,
        height: float = 1.8,
    ):
        """Add a module-card (name, contract, purpose) with accent top border."""

        # Card background with top accent border
        add_filled_box(slide, left, top, width, height)
        # Top accent bar
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.04)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = self.accent_color
        bar.line.fill.background()

        # Scale internal layout proportionally
        pad = 0.10
        name_h = min(0.3, height * 0.2)
        contract_h = min(0.25, height * 0.15)
        y_cursor = top + pad

        # Module name
        name_el = card_el.find(class_="module-name")
        if name_el:
            add_text_box(
                slide,
                get_text(name_el),
                left=left + 0.12,
                top=y_cursor,
                width=width - 0.24,
                height=name_h,
                font_size=max(11, min(15, int(height * 9))),
                bold=True,
                color=self.accent_color,
            )
            y_cursor += name_h

        # Contract (monospace)
        contract_el = card_el.find(class_="module-contract")
        if contract_el:
            add_text_box(
                slide,
                get_text(contract_el),
                left=left + 0.12,
                top=y_cursor,
                width=width - 0.24,
                height=contract_h,
                font_size=max(8, min(10, int(height * 6))),
                font_name=CODE_FONT,
                color=CODE_GREEN,
            )
            y_cursor += contract_h

        # Purpose
        purpose_el = card_el.find(class_="module-purpose")
        remaining = height - (y_cursor - top) - pad
        if purpose_el and remaining > 0.1:
            add_text_box(
                slide,
                get_text(purpose_el),
                left=left + 0.12,
                top=y_cursor,
                width=width - 0.24,
                height=remaining,
                font_size=max(8, min(11, int(height * 6))),
                color=GRAY_70,
            )

    def _add_number_card(
        self,
        slide,
        number: str,
        title: str,
        text: str,
        left: float,
        top: float,
        width: float,
        height: float = 1.8,
    ):
        """Add a card with a big number."""
        add_filled_box(slide, left, top, width, height)

        # Scale internal layout proportionally to card height
        pad = 0.08
        num_h = min(0.7, height * 0.4)
        title_h = min(0.3, height * 0.18)
        num_font = max(24, min(48, int(height * 28)))
        title_font = max(10, min(14, int(height * 8)))
        text_font = max(8, min(10, int(height * 6)))

        add_text_box(
            slide,
            number,
            left=left + 0.1,
            top=top + pad,
            width=width - 0.2,
            height=num_h,
            font_size=num_font,
            bold=True,
            color=MS_CYAN,
            align=PP_ALIGN.CENTER,
        )
        add_text_box(
            slide,
            title,
            left=left + 0.1,
            top=top + pad + num_h,
            width=width - 0.2,
            height=title_h,
            font_size=title_font,
            bold=True,
            color=self.accent_color,
            align=PP_ALIGN.CENTER,
        )
        remaining = height - pad - num_h - title_h - pad
        if remaining > 0.1 and text:
            add_text_box(
                slide,
                text,
                left=left + 0.1,
                top=top + pad + num_h + title_h,
                width=width - 0.2,
                height=remaining,
                font_size=text_font,
                color=GRAY_70,
                align=PP_ALIGN.CENTER,
            )

    # ── Code blocks ──────────────────────────────────────────────────────────

    def _add_code_block(self, slide, code_el: Tag, top: float):
        """Add a code block with syntax highlighting."""
        # Extract structured code runs from HTML spans
        code_runs = self._extract_code_runs(code_el)
        plain_text = get_text(code_el)
        lines = plain_text.count("\n") + 1
        height = max(1.0, min(lines * 0.18 + 0.3, 3.5))

        # Dark background
        add_filled_box(
            slide,
            CONTENT_LEFT,
            top,
            CONTENT_WIDTH,
            height,
            fill_color=CODE_BG,
            border_color=RGBColor(0x30, 0x30, 0x30),
            border_width=1,
            shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
        )

        # Code text with syntax highlighting
        if code_runs:
            box = slide.shapes.add_textbox(
                Inches(CONTENT_LEFT + 0.2),
                Inches(top + 0.12),
                Inches(CONTENT_WIDTH - 0.4),
                Inches(height - 0.24),
            )
            tf = box.text_frame
            tf.word_wrap = True

            # Split runs into lines (paragraphs)
            paragraphs: list[list[dict]] = [[]]
            for r in code_runs:
                parts = r["text"].split("\n")
                for part_idx, part in enumerate(parts):
                    if part_idx > 0:
                        paragraphs.append([])
                    if part:
                        paragraphs[-1].append({**r, "text": part})

            for p_idx, p_runs in enumerate(paragraphs):
                p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
                p.space_before = Pt(0)
                p.space_after = Pt(0)
                if not p_runs:
                    run = p.add_run()
                    run.text = ""
                    _set_font(run, name=CODE_FONT, size=10, color=CODE_DEFAULT)
                else:
                    for r in p_runs:
                        run = p.add_run()
                        run.text = r["text"]
                        _set_font(
                            run,
                            name=CODE_FONT,
                            size=10,
                            bold=r.get("bold", False),
                            color=r.get("color", CODE_DEFAULT),
                        )
        else:
            # Fallback: plain monospace text
            add_text_box(
                slide,
                plain_text,
                left=CONTENT_LEFT + 0.2,
                top=top + 0.12,
                width=CONTENT_WIDTH - 0.4,
                height=height - 0.24,
                font_size=10,
                font_name=CODE_FONT,
                color=CODE_DEFAULT,
            )

    def _extract_code_runs(self, code_el: Tag) -> list[dict]:
        """Extract syntax-highlighted runs from a code block element."""
        el_copy = deepcopy(code_el)
        _replace_br_tags(el_copy)

        color_map = {
            "code-keyword": CODE_BLUE,
            "keyword": CODE_BLUE,
            "code-string": CODE_STRING,
            "string": CODE_STRING,
            "code-comment": CODE_GRAY,
            "comment": CODE_GRAY,
            "code-type": CODE_GREEN,
            "type": CODE_GREEN,
            "code-func": CODE_YELLOW,
            "func": CODE_YELLOW,
            "code-number": CODE_PURPLE,
            "number": CODE_PURPLE,
            "layer-kernel": CODE_BLUE,
            "layer-foundation": CODE_GREEN,
            "layer-apps": CODE_PURPLE,
            "layer-modules": CODE_YELLOW,
        }

        runs: list[dict] = []
        for child in el_copy.descendants:
            if isinstance(child, NavigableString):
                text = str(child)
                if not text:
                    continue
                # Determine color from parent span class
                color = CODE_DEFAULT
                bold = False
                parent = child.parent
                while parent and parent != el_copy:
                    if parent.name == "span":
                        for cls in parent.get("class", []):
                            if cls in color_map:
                                color = color_map[cls]
                                break
                    if parent.name in ("strong", "b"):
                        bold = True
                    parent = parent.parent

                runs.append({"text": text, "color": color, "bold": bold})

        # Merge adjacent runs with identical formatting
        merged: list[dict] = []
        for r in runs:
            if (
                merged
                and merged[-1]["color"] == r["color"]
                and merged[-1]["bold"] == r["bold"]
            ):
                merged[-1]["text"] += r["text"]
            else:
                merged.append(r)

        return merged

    # ── Flow diagrams ────────────────────────────────────────────────────────

    def _add_flow_diagram(self, slide, flow_el: Tag, top: float):
        """Add a flow diagram (flow-box → flow-arrow → flow-box ...)."""
        # Collect steps (flow-box, flow-step, workflow-step)
        steps = flow_el.find_all(class_=["flow-box", "flow-step", "workflow-step"])
        if not steps:
            return

        num_steps = len(steps)
        # Calculate layout
        gap = 0.15
        arrow_width = 0.35
        total_arrows = num_steps - 1
        total_arrow_space = (
            total_arrows * (arrow_width + 2 * gap) if total_arrows > 0 else 0
        )
        remaining = CONTENT_WIDTH - total_arrow_space
        box_width = remaining / num_steps
        box_width = min(box_width, 2.5)
        box_height = 0.9

        # Center the whole diagram
        total_width = num_steps * box_width + total_arrow_space
        start_left = CONTENT_LEFT + (CONTENT_WIDTH - total_width) / 2

        current_left = start_left
        for i, step in enumerate(steps):
            # Step box
            add_filled_box(
                slide,
                current_left,
                top,
                box_width,
                box_height,
                fill_color=DARK_GRAY,
                border_color=self.accent_color,
                border_width=1,
            )

            # Step text
            title_el = step.find(class_=["flow-step-title", "workflow-step-title"])
            desc_el = step.find(class_=["flow-step-desc", "workflow-step-desc"])

            if title_el:
                add_text_box(
                    slide,
                    get_text(title_el),
                    left=current_left + 0.08,
                    top=top + 0.08,
                    width=box_width - 0.16,
                    height=0.35,
                    font_size=12,
                    bold=True,
                    color=WHITE,
                    align=PP_ALIGN.CENTER,
                )
                if desc_el:
                    add_text_box(
                        slide,
                        get_text(desc_el),
                        left=current_left + 0.08,
                        top=top + 0.42,
                        width=box_width - 0.16,
                        height=0.4,
                        font_size=10,
                        color=GRAY_70,
                        align=PP_ALIGN.CENTER,
                    )
            else:
                # Simple text inside box
                text = get_text(step)
                add_text_box(
                    slide,
                    text,
                    left=current_left + 0.08,
                    top=top + 0.08,
                    width=box_width - 0.16,
                    height=box_height - 0.16,
                    font_size=11,
                    color=WHITE,
                    align=PP_ALIGN.CENTER,
                )

            current_left += box_width

            # Arrow between steps
            if i < num_steps - 1:
                arrow_left = current_left + gap
                arrow_top = top + box_height / 2 - 0.12
                add_text_box(
                    slide,
                    "\u2192",
                    left=arrow_left,
                    top=arrow_top,
                    width=arrow_width,
                    height=0.25,
                    font_size=20,
                    bold=True,
                    color=self.accent_color,
                    align=PP_ALIGN.CENTER,
                )
                current_left += arrow_width + 2 * gap

    # ── Notification stacks ──────────────────────────────────────────────────

    def _add_notification_stack(self, slide, stack_el: Tag, top: float):
        """Add a notification stack (allowed/blocked notification items)."""
        notifications = stack_el.find_all(class_="notification")
        if not notifications:
            return

        row_height = 0.55
        row_gap = 0.08
        total_width = 6.0
        start_left = CONTENT_LEFT + (CONTENT_WIDTH - total_width) / 2

        for i, notif in enumerate(notifications):
            ntop = top + i * (row_height + row_gap)
            classes = notif.get("class", [])
            is_allowed = "allowed" in classes
            is_blocked = "blocked" in classes

            # Background
            if is_allowed:
                bg = RGBColor(0x0A, 0x1A, 0x0D)
                border = MS_GREEN
            elif is_blocked:
                bg = RGBColor(0x1A, 0x0A, 0x0A)
                border = MS_RED
            else:
                bg = DARK_GRAY
                border = BORDER_GRAY

            add_filled_box(
                slide,
                start_left,
                ntop,
                total_width,
                row_height,
                fill_color=bg,
                border_color=border,
                border_width=1,
                shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
            )

            # Status icon
            icon = "\u2713" if is_allowed else "\u2715"
            icon_color = MS_GREEN if is_allowed else MS_RED
            add_text_box(
                slide,
                icon,
                left=start_left + 0.1,
                top=ntop + 0.05,
                width=0.35,
                height=0.45,
                font_size=16,
                bold=True,
                color=icon_color,
                align=PP_ALIGN.CENTER,
            )

            # Notification title + body
            title_el = notif.find(class_="notification-title")
            body_el = notif.find(class_="notification-body")
            title = get_text(title_el) if title_el else ""
            body = get_text(body_el) if body_el else ""

            add_text_box(
                slide,
                title,
                left=start_left + 0.5,
                top=ntop + 0.04,
                width=total_width - 0.7,
                height=0.25,
                font_size=12,
                bold=True,
                color=WHITE,
            )
            add_text_box(
                slide,
                body,
                left=start_left + 0.5,
                top=ntop + 0.27,
                width=total_width - 0.70,
                height=0.25,
                font_size=10,
                color=GRAY_70,
            )

    # ── Comparison table (two-column grid, not HTML <table>) ─────────────────

    def _add_comparison_table(self, slide, comp_el: Tag, top: float):
        """Add a comparison-table (CSS grid with .header .left .right cells)."""
        children = [c for c in comp_el.children if isinstance(c, Tag)]
        if not children:
            return

        col_width = CONTENT_WIDTH / 2
        row_height = 0.32
        current_row_top = top

        for child in children:
            classes = child.get("class", [])
            text = get_text(child)
            is_header = "header" in classes
            is_left = "left" in classes
            is_right = "right" in classes

            if is_header and is_left:
                add_text_box(
                    slide,
                    text,
                    left=CONTENT_LEFT,
                    top=current_row_top,
                    width=col_width,
                    height=row_height,
                    font_size=13,
                    bold=True,
                    color=self.accent_color,
                )
            elif is_header and is_right:
                add_text_box(
                    slide,
                    text,
                    left=CONTENT_LEFT + col_width,
                    top=current_row_top,
                    width=col_width,
                    height=row_height,
                    font_size=13,
                    bold=True,
                    color=CODE_GREEN,
                )
                current_row_top += row_height + 0.05
            elif is_left:
                add_text_box(
                    slide,
                    text,
                    left=CONTENT_LEFT,
                    top=current_row_top,
                    width=col_width,
                    height=row_height,
                    font_size=11,
                    color=WHITE,
                )
            elif is_right:
                add_text_box(
                    slide,
                    text,
                    left=CONTENT_LEFT + col_width,
                    top=current_row_top,
                    width=col_width,
                    height=row_height,
                    font_size=11,
                    color=GRAY_70,
                )
                current_row_top += row_height

    # ── Architecture diagram ─────────────────────────────────────────────────

    def _add_architecture_diagram(self, slide, arch_el: Tag, top: float):
        """Add an architecture diagram (text art with colored spans)."""
        runs = self._extract_code_runs(arch_el)
        if not runs:
            plain = get_text(arch_el)
            add_text_box(
                slide,
                plain,
                left=CONTENT_LEFT,
                top=top,
                width=CONTENT_WIDTH,
                height=3.0,
                font_size=11,
                font_name=CODE_FONT,
                color=CODE_DEFAULT,
            )
            return

        # Use code block rendering
        plain_text = get_text(arch_el)
        lines = plain_text.count("\n") + 1
        height = max(1.5, min(lines * 0.18 + 0.3, 3.5))

        add_filled_box(
            slide,
            CONTENT_LEFT,
            top,
            CONTENT_WIDTH,
            height,
            fill_color=CODE_BG,
            border_color=RGBColor(0x30, 0x30, 0x30),
            border_width=1,
            shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
        )

        box = slide.shapes.add_textbox(
            Inches(CONTENT_LEFT + 0.2),
            Inches(top + 0.12),
            Inches(CONTENT_WIDTH - 0.4),
            Inches(height - 0.24),
        )
        tf = box.text_frame
        tf.word_wrap = True

        paragraphs: list[list[dict]] = [[]]
        for r in runs:
            parts = r["text"].split("\n")
            for part_idx, part in enumerate(parts):
                if part_idx > 0:
                    paragraphs.append([])
                if part:
                    paragraphs[-1].append({**r, "text": part})

        for p_idx, p_runs in enumerate(paragraphs):
            p = tf.paragraphs[0] if p_idx == 0 else tf.add_paragraph()
            p.space_before = Pt(0)
            p.space_after = Pt(0)
            if not p_runs:
                run = p.add_run()
                run.text = ""
                _set_font(run, name=CODE_FONT, size=10, color=CODE_DEFAULT)
            else:
                for r in p_runs:
                    run = p.add_run()
                    run.text = r["text"]
                    _set_font(
                        run,
                        name=CODE_FONT,
                        size=10,
                        bold=r.get("bold", False),
                        color=r.get("color", CODE_DEFAULT),
                    )

    # ── Tenets ───────────────────────────────────────────────────────────────

    def _add_tenets(self, slide, tenets: list[Tag], top: float):
        """Add tenet boxes to the slide."""
        num_tenets = len(tenets)
        if num_tenets >= 4:
            for i, tenet in enumerate(tenets):
                col = i % 2
                row = i // 2
                self._add_single_tenet(
                    slide, tenet, CONTENT_LEFT + col * 4.5, top + row * 1.0, width=4.2
                )
        else:
            for i, tenet in enumerate(tenets):
                self._add_single_tenet(
                    slide, tenet, CONTENT_LEFT, top + i * 1.0, width=CONTENT_WIDTH
                )

    def _add_single_tenet(
        self, slide, tenet: Tag, left: float, top: float, width: float
    ):
        """Add a single tenet box."""
        title_el = tenet.find(class_="tenet-title")
        text_el = tenet.find(class_="tenet-text")
        title = get_text(title_el) if title_el else ""
        text = get_text(text_el) if text_el else ""
        classes = tenet.get("class", [])
        accent_color = parse_color_from_class(classes) or MS_GREEN
        add_tenet(slide, title, text, left, top, width=width, accent_color=accent_color)

    # ── Versus comparison ────────────────────────────────────────────────────

    def _add_versus(self, slide, versus: Tag, top: float):
        """Add a versus comparison layout."""
        sides = versus.find_all(class_="versus-side")
        if len(sides) < 2:
            return

        for side_idx, side in enumerate(sides):
            base_left = CONTENT_LEFT if side_idx == 0 else 5.5

            title_el = side.find(class_="versus-title")
            if title_el:
                classes = title_el.get("class", [])
                color = parse_color_from_class(classes) or (
                    MS_ORANGE if side_idx == 0 else MS_GREEN
                )
                add_text_box(
                    slide,
                    get_text(title_el),
                    left=base_left,
                    top=top,
                    width=4.0,
                    height=0.4,
                    font_size=24,
                    bold=True,
                    color=color,
                )

            items_list = side.find(class_="feature-list")
            if items_list:
                for i, item in enumerate(items_list.find_all("li")):
                    text = get_text(item)
                    if "\u2713" in text:
                        color = MS_GREEN
                    elif "\u2717" in text:
                        color = MS_RED
                    else:
                        color = WHITE
                    add_text_box(
                        slide,
                        text,
                        left=base_left,
                        top=top + 0.5 + i * 0.35,
                        width=4.0,
                        height=0.35,
                        font_size=14,
                        color=color,
                    )

        # VS divider
        add_text_box(
            slide,
            "vs",
            left=4.5,
            top=top + 1.2,
            width=1.0,
            height=0.5,
            font_size=32,
            bold=True,
            color=GRAY_50,
            align=PP_ALIGN.CENTER,
        )

    # ── Tables ───────────────────────────────────────────────────────────────

    def _add_table(self, slide, table: Tag, top: float):
        """Add a data table to the slide."""
        rows = table.find_all("tr")
        if not rows:
            return

        row_height = 0.32
        for row_idx, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            is_header = row.find("th") is not None
            num_cols = len(cells)

            # Calculate column widths
            if num_cols == 0:
                continue
            col_widths = [CONTENT_WIDTH / num_cols] * num_cols
            if num_cols == 3:
                col_widths = [2.5, 2.5, 3.4]
            elif num_cols == 2:
                col_widths = [4.2, 4.2]

            left = CONTENT_LEFT
            for col_idx, cell in enumerate(cells):
                text = get_text(cell)
                width = col_widths[col_idx] if col_idx < len(col_widths) else 2.0

                if is_header:
                    color = self.accent_color
                    font_size = 12
                    bold = True
                else:
                    if col_idx == 0:
                        color = WHITE
                        bold = True
                    else:
                        color = GRAY_70
                        bold = False
                    font_size = 11

                    if "\u2713" in text:
                        color = MS_GREEN
                    elif "\u2717" in text:
                        color = MS_RED
                    elif "~" in text:
                        color = MS_ORANGE

                # Check for inline accent color (style attribute)
                style = cell.get("style", "")
                if "color:" in style and "var(--accent)" in style:
                    color = self.accent_color
                    bold = True

                add_text_box(
                    slide,
                    text,
                    left=left,
                    top=top + row_idx * row_height,
                    width=width,
                    height=row_height,
                    font_size=font_size,
                    bold=bold,
                    color=color,
                )
                left += width

    # ── Feature lists ────────────────────────────────────────────────────────

    def _add_feature_list(self, slide, feature_list: Tag, top: float):
        """Add a feature list to the slide."""
        items = feature_list.find_all("li")
        for i, item in enumerate(items):
            text = get_text(item)
            if "\u2713" in text:
                color = MS_GREEN
            elif "\u2717" in text:
                color = MS_RED
            else:
                color = WHITE
            add_text_box(
                slide,
                text,
                left=CONTENT_LEFT,
                top=top + i * 0.4,
                width=CONTENT_WIDTH,
                height=0.4,
                font_size=16,
                color=color,
            )

    # ── Stats grid/row ───────────────────────────────────────────────────────

    def _add_stats(self, slide, stat_container: Tag, top: float):
        """Add a stats grid or stat row to the slide."""
        stats = stat_container.find_all(class_="stat")
        num_stats = len(stats)
        if num_stats == 0:
            return

        width_per_stat = CONTENT_WIDTH / num_stats
        start_left = CONTENT_LEFT

        for i, stat in enumerate(stats):
            # Try both naming conventions
            number_el = stat.find(class_="stat-number") or stat.find(
                class_="stat-value"
            )
            label_el = stat.find(class_="stat-label")

            number = get_text(number_el) if number_el else ""
            label = get_text(label_el) if label_el else ""

            left = start_left + i * width_per_stat

            add_text_box(
                slide,
                number,
                left=left,
                top=top,
                width=width_per_stat,
                height=0.6,
                font_size=40,
                bold=True,
                color=MS_CYAN,
                align=PP_ALIGN.CENTER,
            )
            add_text_box(
                slide,
                label,
                left=left,
                top=top + 0.6,
                width=width_per_stat,
                height=0.4,
                font_size=12,
                color=GRAY_70,
                align=PP_ALIGN.CENTER,
            )

    # ── Quote ────────────────────────────────────────────────────────────────

    def _add_quote(self, slide, quote: Tag, top: float):
        """Add a quote to the slide."""
        text = get_text(quote)
        add_text_box(
            slide,
            f'"{text}"',
            left=CONTENT_LEFT,
            top=top,
            width=CONTENT_WIDTH,
            height=1.2,
            font_size=24,
            italic=True,
            color=WHITE,
            align=PP_ALIGN.CENTER,
        )
        attribution = quote.find_next_sibling(class_="quote-attribution")
        if attribution:
            add_text_box(
                slide,
                get_text(attribution),
                left=CONTENT_LEFT,
                top=top + 1.2,
                width=CONTENT_WIDTH,
                height=0.3,
                font_size=14,
                color=GRAY_50,
                align=PP_ALIGN.CENTER,
            )

    # ── Convert & Save ───────────────────────────────────────────────────────

    def convert(self) -> Presentation:
        """Convert the HTML to a PowerPoint presentation."""
        slides = self.extract_slides()

        if not slides:
            warnings.warn(
                "No slides found in HTML. Check for <div class='slide'> or <section class='slide'> elements."
            )

        for i, slide_div in enumerate(slides):
            self.process_slide(slide_div, i + 1)

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):", file=sys.stderr)
            for w in self.warnings:
                print(f"  - {w}", file=sys.stderr)

        return self.prs

    def save(self, output_path: str):
        """Save the presentation to a file."""
        self.prs.save(output_path)


# ── CLI entry point ──────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Convert Amplifier Stories HTML decks to PowerPoint presentations."
    )
    parser.add_argument("input", help="Input HTML file path")
    parser.add_argument(
        "output", nargs="?", help="Output PPTX file path (default: same name as input)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".pptx")

    print(f"Converting: {input_path}")
    print(f"Output: {output_path}")

    html_content = input_path.read_text(encoding="utf-8")
    converter = HTMLToPPTXConverter(html_content)
    converter.convert()
    converter.save(str(output_path))

    num_slides = len(converter.prs.slides)
    print(f"Done! Created {output_path} ({num_slides} slides)")


if __name__ == "__main__":
    main()
