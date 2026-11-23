#!/usr/bin/env python3
"""Convert project markdown files to Word (.docx) using python-docx."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.table import _Cell


def set_cell_shading(cell: _Cell, fill: str) -> None:
    shading = cell._element.get_or_add_tcPr()
    shd = shading.makeelement(
        qn("w:shd"),
        {
            qn("w:fill"): fill,
            qn("w:val"): "clear",
        },
    )
    shading.append(shd)


def add_formatted_runs(paragraph, text: str) -> None:
    pattern = re.compile(
        r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|[^*`[]+)"
    )
    for chunk in pattern.findall(text):
        if chunk.startswith("**") and chunk.endswith("**"):
            run = paragraph.add_run(chunk[2:-2])
            run.bold = True
        elif chunk.startswith("*") and chunk.endswith("*"):
            run = paragraph.add_run(chunk[1:-1])
            run.italic = True
        elif chunk.startswith("`") and chunk.endswith("`"):
            run = paragraph.add_run(chunk[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        elif chunk.startswith("[") and "](" in chunk:
            match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", chunk)
            if match:
                run = paragraph.add_run(match.group(1))
                run.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
                run.underline = True
        else:
            paragraph.add_run(chunk)


def parse_table_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\|?[\s\-:|]+\|?$", line.strip()))


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return

    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"

    for row_idx, row in enumerate(rows):
        for col_idx, value in enumerate(row):
            cell = table.rows[row_idx].cells[col_idx]
            cell.text = ""
            paragraph = cell.paragraphs[0]
            add_formatted_runs(paragraph, value)
            if row_idx == 0:
                for run in paragraph.runs:
                    run.bold = True
                set_cell_shading(cell, "E7E6E6")

    doc.add_paragraph("")


def add_code_block(doc: Document, lines: list[str]) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.25)
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(6)
    run = paragraph.add_run("\n".join(lines))
    run.font.name = "Consolas"
    run.font.size = Pt(9)


def add_blockquote(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.35)
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(4)
    add_formatted_runs(paragraph, text)
    for run in paragraph.runs:
        run.italic = True
        run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)


def convert_markdown_to_docx(md_path: Path, docx_path: Path) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    i = 0
    list_buffer: list[tuple[str, str]] = []
    code_buffer: list[str] | None = None

    def flush_list() -> None:
        nonlocal list_buffer
        for kind, item in list_buffer:
            paragraph = doc.add_paragraph(style="List Bullet" if kind == "bullet" else "List Number")
            add_formatted_runs(paragraph, item)
        list_buffer = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if code_buffer is not None:
            if stripped.startswith("```"):
                add_code_block(doc, code_buffer)
                code_buffer = None
            else:
                code_buffer.append(line)
            i += 1
            continue

        if stripped.startswith("```"):
            flush_list()
            code_buffer = []
            i += 1
            continue

        if not stripped:
            flush_list()
            i += 1
            continue

        if stripped == "---":
            flush_list()
            doc.add_paragraph("")
            i += 1
            continue

        if stripped.startswith("#"):
            flush_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            heading = doc.add_heading(title, level=min(level, 4))
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
            i += 1
            continue

        if stripped.startswith(">"):
            flush_list()
            quote_lines = [stripped.lstrip(">").strip()]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            add_blockquote(doc, " ".join(quote_lines))
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            flush_list()
            table_rows = [parse_table_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_rows.append(parse_table_row(lines[i]))
                i += 1
            add_table(doc, table_rows)
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet_match:
            list_buffer.append(("bullet", bullet_match.group(1)))
            i += 1
            continue

        number_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if number_match:
            list_buffer.append(("number", number_match.group(1)))
            i += 1
            continue

        flush_list()
        paragraph = doc.add_paragraph()
        add_formatted_runs(paragraph, stripped)
        i += 1

    flush_list()
    if code_buffer is not None:
        add_code_block(doc, code_buffer)

    doc.save(docx_path)


def main(argv: list[str]) -> int:
    base = Path(__file__).resolve().parent
    targets = argv[1:] or ["landing-concept.md", "landing-content-brief.md"]

    for name in targets:
        md_path = base / name
        if not md_path.exists():
            print(f"Skip missing file: {md_path}")
            continue
        docx_path = md_path.with_suffix(".docx")
        convert_markdown_to_docx(md_path, docx_path)
        print(f"Created: {docx_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
