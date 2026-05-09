# pdf_report.py
# Generates a styled PDF report using reportlab.
# Chosen over weasyprint (requires system deps) and pdfkit/puppeteer (headless browser).
# reportlab is pure-Python, pip-installable, and sufficient for structured reports.

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

BAND_COLORS_HEX = {
    "High":   colors.HexColor("#1D9E75"),
    "Medium": colors.HexColor("#BA7517"),
    "Low":    colors.HexColor("#E24B4A"),
}

BRAND_DARK  = colors.HexColor("#1A1A2E")
BRAND_MID   = colors.HexColor("#4A4A6A")
BRAND_LIGHT = colors.HexColor("#F5F4F0")
ACCENT      = colors.HexColor("#534AB7")


def build_pdf(name: str, scores: dict) -> bytes:
    """Returns PDF as bytes."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontSize=26,
        leading=32,
        textColor=BRAND_DARK,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=13,
        leading=18,
        textColor=BRAND_MID,
        fontName="Helvetica",
    )
    section_heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontSize=14,
        leading=18,
        textColor=BRAND_DARK,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=BRAND_MID,
        fontName="Helvetica",
    )
    band_label_style = ParagraphStyle(
        "BandLabel",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("Leadership Assessment", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Personal report for <b>{name}</b>", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=ACCENT))
    story.append(Spacer(1, 12))

    # ── Overall score ────────────────────────────────────────────────────────────
    total = scores["total_score"]
    total_max = scores["total_max"]
    pct = scores["overall_percentage"]

    overall_data = [
        [
            Paragraph("Overall Score", ParagraphStyle("OL", parent=styles["Normal"], fontSize=11, textColor=BRAND_MID, fontName="Helvetica")),
            Paragraph(f"<b>{total} / {total_max}</b>", ParagraphStyle("OR", parent=styles["Normal"], fontSize=16, textColor=BRAND_DARK, fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(f"<b>{pct}%</b>", ParagraphStyle("OP", parent=styles["Normal"], fontSize=16, textColor=ACCENT, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        ]
    ]

    overall_table = Table(overall_data, colWidths=["50%", "25%", "25%"])
    overall_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_LIGHT]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(overall_table)
    story.append(Spacer(1, 20))

    # ── Dimension sections ───────────────────────────────────────────────────────
    for dim in scores["dimensions"]:
        band_color = BAND_COLORS_HEX.get(dim["band"], BRAND_MID)

        # Dimension heading row
        heading_data = [[
            Paragraph(dim["label"], section_heading_style),
            Paragraph(
                f"<b>{dim['score']} / {dim['max_score']}</b>",
                ParagraphStyle("DimScore", parent=styles["Normal"], fontSize=12,
                               fontName="Helvetica-Bold", textColor=BRAND_DARK, alignment=TA_CENTER)
            ),
            Paragraph(
                dim["band"],
                ParagraphStyle("DimBand", parent=styles["Normal"], fontSize=11,
                               fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)
            ),
        ]]

        heading_table = Table(heading_data, colWidths=["55%", "20%", "25%"])
        heading_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (1, 0), colors.white),
            ("BACKGROUND", (2, 0), (2, 0), band_color),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#EEEEEE")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(heading_table)

        # Progress bar (approximated with a filled table row)
        bar_pct = dim["percentage"]
        bar_width_total = 170 * mm
        filled = bar_width_total * bar_pct / 100
        empty  = bar_width_total - filled

        bar_data = [[""]]
        bar_table = Table(bar_data, colWidths=[filled])
        bar_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), band_color),
            ("ROWHEIGHT", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))

        container_data = [[bar_table, ""]]
        container_table = Table(container_data, colWidths=[filled, empty if empty > 0 else 0.1])
        container_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEEEEE")),
            ("ROWHEIGHT", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ]))
        story.append(container_table)

        # Feedback text
        story.append(Spacer(1, 6))
        story.append(Paragraph(dim["feedback"], body_style))
        story.append(Spacer(1, 16))

    # ── Footer ───────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Generated by Planet Ganges Consulting · Leadership Assessment Platform",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                       textColor=colors.HexColor("#AAAAAA"), fontName="Helvetica", alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()