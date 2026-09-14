import html
from io import BytesIO

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from services.quotation_calculator import amount_in_words, calculate_quotation
from services.quotation_data import default_quotation


# ============================================================
# PAGE CONFIG / THEME
# ============================================================

st.set_page_config(
    page_title="Solar Quotation Generator",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px;}
        .app-hero {
            padding: 1.35rem 1.6rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #073b4c 0%, #0b6e69 52%, #f4a261 100%);
            color: white;
            margin-bottom: 1rem;
        }
        .app-hero h1 {margin: 0; font-size: 2.25rem;}
        .app-hero p {margin: .35rem 0 0; opacity: .92;}
        .step-card {
            padding: .8rem 1rem;
            border: 1px solid #dce5e8;
            border-radius: 14px;
            background: #f8fbfc;
            margin-bottom: .8rem;
        }
        .section-title {font-size: 1.15rem; font-weight: 700; margin-top: .5rem;}
        div[data-testid="stMetricValue"] {font-size: 1.35rem;}
        .footer-note {text-align:center; color:#6b7280; font-size:.82rem; margin-top:1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE / NAVIGATION
# ============================================================

PAGES = [
    ("Company & Client", "👤"),
    ("Solar System", "☀️"),
    ("Items & Services", "🧰"),
    ("Optional Items", "➕"),
    ("Pricing", "💰"),
    ("Terms & Conditions", "📋"),
    ("Generate Quotation", "📄"),
]

if "quotation" not in st.session_state:
    st.session_state.quotation = default_quotation()
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "widget_version" not in st.session_state:
    st.session_state.widget_version = 0
if "generated_pdf" not in st.session_state:
    st.session_state.generated_pdf = None

q = st.session_state.quotation


def key(name):
    return f"q_v{st.session_state.widget_version}_{name}"


def go_next():
    st.session_state.current_page = min(len(PAGES) - 1, st.session_state.current_page + 1)


def go_previous():
    st.session_state.current_page = max(0, st.session_state.current_page - 1)


def reset_quotation():
    st.session_state.quotation = default_quotation()
    st.session_state.current_page = 0
    st.session_state.widget_version += 1
    st.session_state.generated_pdf = None


def money(value):
    return f"PKR {float(value):,.0f}"


# ============================================================
# PDF GENERATOR — INTERNATIONAL STANDARD, COLORFUL
# ============================================================

NAVY = colors.HexColor("#073B4C")
TEAL = colors.HexColor("#0B6E69")
ORANGE = colors.HexColor("#F4A261")
GOLD = colors.HexColor("#E9C46A")
LIGHT = colors.HexColor("#F4F8F9")
MID = colors.HexColor("#D9E6EA")
DARK = colors.HexColor("#263238")
GREEN = colors.HexColor("#2A9D8F")
RED = colors.HexColor("#C94C4C")
WHITE = colors.white


def _esc(value):
    return html.escape("" if value is None else str(value)).replace("\n", "<br/>")


def _pdf_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4

    # Top brand bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
    canvas.setFillColor(ORANGE)
    canvas.rect(0, height - 9 * mm, 55 * mm, 9 * mm, fill=1, stroke=0)

    # Footer
    canvas.setStrokeColor(MID)
    canvas.line(14 * mm, 13 * mm, width - 14 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#65747B"))
    canvas.drawString(14 * mm, 8.5 * mm, "Solar Quotation • Professional Proposal")
    canvas.drawRightString(width - 14 * mm, 8.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _pdf_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PdfTitle", parent=styles["Title"], fontName="Helvetica-Bold",
            fontSize=25, leading=28, textColor=NAVY, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "PdfSubtitle", parent=styles["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=13, textColor=colors.HexColor("#5F6F76"),
        ),
        "h1": ParagraphStyle(
            "PdfH1", parent=styles["Heading1"], fontName="Helvetica-Bold",
            fontSize=15, leading=18, textColor=NAVY, spaceBefore=4, spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "PdfH2", parent=styles["Heading2"], fontName="Helvetica-Bold",
            fontSize=10.5, leading=13, textColor=TEAL, spaceBefore=4, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "PdfBody", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=8.4, leading=12, textColor=DARK,
        ),
        "small": ParagraphStyle(
            "PdfSmall", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=7.2, leading=9.5, textColor=DARK,
        ),
        "small_white": ParagraphStyle(
            "PdfSmallWhite", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=7.6, leading=10, textColor=WHITE,
        ),
        "center": ParagraphStyle(
            "PdfCenter", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=8.2, leading=11, textColor=DARK, alignment=TA_CENTER,
        ),
        "right": ParagraphStyle(
            "PdfRight", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=8.2, leading=11, textColor=DARK, alignment=TA_RIGHT,
        ),
        "total": ParagraphStyle(
            "PdfTotal", parent=styles["BodyText"], fontName="Helvetica-Bold",
            fontSize=13, leading=16, textColor=WHITE, alignment=TA_RIGHT,
        ),
    }


def _label_value(label, value, styles):
    return Paragraph(f"<b>{_esc(label)}</b><br/>{_esc(value) or '—'}", styles["small"])


def generate_international_pdf(q):
    calc = calculate_quotation(q)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=13 * mm,
        leftMargin=13 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title=f"Solar Quotation {q['quotation_number']}",
        author=q["company"].get("name") or "Solar Company",
        subject="Solar PV Quotation",
    )
    s = _pdf_styles()
    story = []
    company = q["company"]
    client = q["client"]

    # ---------- Cover / executive summary ----------
    story.append(Spacer(1, 9 * mm))
    brand = Table(
        [[
            Paragraph("<b>☀ SOLAR</b>", ParagraphStyle("brand", fontName="Helvetica-Bold", fontSize=19, textColor=WHITE)),
            Paragraph("<b>PROFESSIONAL QUOTATION</b><br/><font size='8'>Solar PV • Engineering • Installation</font>", s["small_white"]),
        ]],
        colWidths=[60 * mm, 105 * mm],
        rowHeights=[18 * mm],
    )
    brand.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), NAVY),
        ("BACKGROUND", (1, 0), (1, 0), TEAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(brand)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("SOLAR PV QUOTATION", s["title"]))
    story.append(Paragraph(
        f"Prepared for <b>{_esc(client.get('name') or 'Valued Client')}</b> • Quotation No. <b>{_esc(q['quotation_number'])}</b> • {_esc(q['quotation_date'])}",
        s["subtitle"],
    ))
    story.append(Spacer(1, 6 * mm))

    summary_cards = [
        [Paragraph(f"<b>{calc['pv_kwp']:.2f} kWp</b><br/><font size='7'>PV CAPACITY</font>", s["center"]),
         Paragraph(f"<b>{calc['inverter_kw']:.2f} kW</b><br/><font size='7'>INVERTER</font>", s["center"]),
         Paragraph(f"<b>{calc['battery_kwh']:.2f} kWh</b><br/><font size='7'>BATTERY</font>", s["center"]),
         Paragraph(f"<b>{money(calc['grand_total'])}</b><br/><font size='7'>PROJECT VALUE</font>", s["center"])],
    ]
    cards = Table(summary_cards, colWidths=[41 * mm] * 4, rowHeights=[23 * mm])
    cards.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E7F3F2")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FFF2E5")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#EEF3F7")),
        ("BACKGROUND", (3, 0), (3, 0), NAVY),
        ("TEXTCOLOR", (3, 0), (3, 0), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.5, MID),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(cards)
    story.append(Spacer(1, 8 * mm))

    parties = Table([
        [_label_value("Prepared By", company.get("name"), s), _label_value("Client", client.get("name"), s)],
        [_label_value("Company Address", company.get("address"), s), _label_value("Project / Site", client.get("address"), s)],
        [_label_value("Contact", " • ".join(x for x in [company.get("phone"), company.get("email"), company.get("website")] if x), s),
         _label_value("Client Contact", " • ".join(x for x in [client.get("phone"), client.get("email")] if x), s)],
    ], colWidths=[82.5 * mm, 82.5 * mm])
    parties.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.6, MID),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, MID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(parties)
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "This proposal presents the recommended solar PV configuration, scope of supply, commercial pricing, optional services and key terms for the proposed installation.",
        s["body"],
    ))

    # ---------- System design ----------
    story.append(PageBreak())
    story.append(Paragraph("1. SYSTEM DESIGN & EQUIPMENT", s["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=6))

    equipment = [[
        Paragraph("Category", s["small_white"]), Paragraph("Specification", s["small_white"]),
        Paragraph("Qty", s["small_white"]), Paragraph("Unit", s["small_white"]), Paragraph("Unit Price", s["small_white"]),
    ]]

    def eqrow(category, specification, qty, unit, price):
        equipment.append([
            Paragraph(_esc(category), s["small"]), Paragraph(_esc(specification), s["small"]),
            Paragraph(_esc(qty), s["center"]), Paragraph(_esc(unit), s["center"]),
            Paragraph(money(price), s["right"]),
        ])

    eqrow("Solar PV Modules", f"{q['panels']['manufacturer']} {q['panels']['model']} • {q['panels']['wattage']:g} W • {q['panels']['description']}", q["panels"]["quantity"], "pcs", q["panels"]["unit_price"])
    eqrow("Inverter", f"{q['inverter']['manufacturer']} {q['inverter']['model']} • {q['inverter']['type']} • {q['inverter']['capacity_kw']:g} kW", q["inverter"]["quantity"], "pcs", q["inverter"]["unit_price"])
    if q["battery"]["required"]:
        eqrow("Battery", f"{q['battery']['manufacturer']} {q['battery']['model']} • {q['battery']['type']} • {q['battery']['capacity_kwh']:g} kWh", q["battery"]["quantity"], "pcs", q["battery"]["unit_price"])

    eq_table = Table(equipment, colWidths=[31 * mm, 79 * mm, 15 * mm, 15 * mm, 30 * mm], repeatRows=1)
    eq_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, MID),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(eq_table)
    story.append(Spacer(1, 7 * mm))

    design = Table([
        [Paragraph("SYSTEM METRICS", s["small_white"]), Paragraph("PROJECT CONFIGURATION", s["small_white"])],
        [Paragraph(f"<b>{calc['pv_kwp']:.2f} kWp</b><br/>Total PV capacity", s["small"]), Paragraph(f"<b>{calc['inverter_kw']:.2f} kW</b><br/>Total inverter capacity", s["small"])],
        [Paragraph(f"<b>{calc['battery_kwh']:.2f} kWh</b><br/>Usable nominal battery capacity", s["small"]), Paragraph(f"<b>{_esc(q['inverter']['type'])}</b><br/>Inverter architecture", s["small"])],
    ], colWidths=[82.5 * mm, 82.5 * mm])
    design.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F2F8F7")),
        ("GRID", (0, 0), (-1, -1), 0.4, MID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(design)

    # ---------- Scope and commercial BOQ ----------
    story.append(PageBreak())
    story.append(Paragraph("2. SCOPE OF SUPPLY & COMMERCIAL SCHEDULE", s["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=6))

    rows = [[
        Paragraph("#", s["small_white"]), Paragraph("Scope", s["small_white"]), Paragraph("Description", s["small_white"]),
        Paragraph("Qty", s["small_white"]), Paragraph("Unit Price", s["small_white"]), Paragraph("Amount", s["small_white"]),
    ]]
    n = 1

    def add_scope(scope, description, qty, price):
        nonlocal n
        amount = float(qty) * float(price)
        rows.append([
            Paragraph(str(n), s["center"]), Paragraph(_esc(scope), s["small"]), Paragraph(_esc(description), s["small"]),
            Paragraph(f"{qty:g}", s["right"]), Paragraph(money(price), s["right"]), Paragraph(money(amount), s["right"]),
        ])
        n += 1

    add_scope("Solar Panels", q["panels"]["description"], q["panels"]["quantity"], q["panels"]["unit_price"])
    add_scope("Inverter", f"{q['inverter']['type']} inverter", q["inverter"]["quantity"], q["inverter"]["unit_price"])
    if q["battery"]["required"]:
        add_scope("Battery", f"{q['battery']['type']} battery", q["battery"]["quantity"], q["battery"]["unit_price"])

    for item_key, label in [
        ("structure", "Solar Structure"), ("cables", "Cables"), ("bos", "Protection & BOS"),
        ("civil", "Civil Work"), ("transportation", "Transportation"), ("other", "Other / Miscellaneous"),
    ]:
        item = q[item_key]
        if item.get("included"):
            add_scope(label, item.get("description", ""), float(item.get("quantity", 0)), float(item.get("unit_price", 0)))

    add_scope("Installation", "Standard installation, commissioning and testing", 1, calc["installation_cost"])

    boq = Table(rows, colWidths=[9 * mm, 29 * mm, 69 * mm, 14 * mm, 25 * mm, 28 * mm], repeatRows=1)
    boq.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.35, MID),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(boq)
    story.append(Spacer(1, 6 * mm))

    # ---------- Optional services ----------
    story.append(Paragraph("Optional Services", s["h2"]))
    opt_rows = [[
        Paragraph("Service", s["small_white"]), Paragraph("Description", s["small_white"]), Paragraph("Qty", s["small_white"]),
        Paragraph("Price", s["small_white"]), Paragraph("Commercial Status", s["small_white"]),
    ]]
    for item in q["optional"].values():
        status = "Included in Total" if item["include"] else "Optional / Excluded"
        opt_rows.append([
            Paragraph(_esc(item["type"]), s["small"]), Paragraph(_esc(item["description"]), s["small"]),
            Paragraph(str(item["quantity"]), s["center"]), Paragraph(money(item["unit_price"]), s["right"]),
            Paragraph(status, s["small"]),
        ])
    opt_table = Table(opt_rows, colWidths=[36 * mm, 73 * mm, 14 * mm, 25 * mm, 26 * mm], repeatRows=1)
    opt_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("GRID", (0, 0), (-1, -1), 0.35, MID),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (2, 1), (3, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(opt_table)

    # ---------- Commercial summary ----------
    story.append(PageBreak())
    story.append(Paragraph("3. COMMERCIAL SUMMARY", s["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=6))

    totals = [
        [Paragraph("Main Equipment & Services", s["body"]), Paragraph(money(calc["main_subtotal"]), s["right"])],
        [Paragraph("Included Optional Services", s["body"]), Paragraph(money(calc["included_optional"]), s["right"])],
        [Paragraph("Subtotal", s["body"]), Paragraph(money(calc["subtotal"]), s["right"])],
        [Paragraph("Discount", s["body"]), Paragraph(f"- {money(calc['discount'])}", s["right"])],
        [Paragraph(f"Tax ({float(q['tax_rate']):g}%)", s["body"]), Paragraph(money(calc["tax"]), s["right"])],
    ]
    total_table = Table(totals, colWidths=[105 * mm, 60 * mm])
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.45, MID),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 2 * mm))

    grand = Table([[Paragraph("GRAND TOTAL", s["small_white"]), Paragraph(money(calc["grand_total"]), s["total"])]], colWidths=[105 * mm, 60 * mm], rowHeights=[18 * mm])
    grand.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BACKGROUND", (0, 0), (0, 0), TEAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(grand)
    story.append(Spacer(1, 5 * mm))

    words_box = Table([[Paragraph(f"<b>Amount in Words</b><br/>{_esc(amount_in_words(calc['grand_total']))}", s["body"])]], colWidths=[165 * mm])
    words_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7EA")),
        ("BOX", (0, 0), (-1, -1), 0.7, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(words_box)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("Commercial Notes", s["h2"]))
    notes = [
        f"Discount method: {_esc(q['discount_type'])} — {float(q['discount_value']):g}",
        f"Installation method: {_esc(q['installation']['mode'])}",
        "Optional services are excluded from the Grand Total unless specifically marked as included.",
        "All monetary values are presented in Pakistani Rupees (PKR).",
    ]
    for note in notes:
        story.append(Paragraph("• " + note, s["body"]))

    # ---------- Terms + signatures ----------
    story.append(PageBreak())
    story.append(Paragraph("4. TERMS, CONDITIONS & ACCEPTANCE", s["h1"]))
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=6))

    term_lines = [x.strip() for x in q["terms"].splitlines() if x.strip()]
    for line in term_lines:
        safe = _esc(line)
        story.append(Paragraph(safe, s["body"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 8 * mm))
    acceptance = Table([
        [Paragraph("CUSTOMER ACCEPTANCE", s["small_white"]), Paragraph("FOR COMPANY", s["small_white"])],
        [Paragraph("\n\nName: ________________________________<br/><br/>Signature: ____________________________<br/><br/>Date: _________________________________", s["small"]),
         Paragraph("\n\nAuthorized By: _________________________<br/><br/>Signature: ____________________________<br/><br/>Date: _________________________________", s["small"])],
    ], colWidths=[82.5 * mm, 82.5 * mm], rowHeights=[9 * mm, 42 * mm])
    acceptance.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), TEAL),
        ("BACKGROUND", (1, 0), (1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, MID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(acceptance)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph(
        "Thank you for the opportunity to submit this proposal. We look forward to delivering a safe, reliable and high-quality solar energy solution.",
        ParagraphStyle("thanks", parent=s["body"], alignment=TA_CENTER, textColor=TEAL, fontName="Helvetica-Bold"),
    ))

    doc.build(story, onFirstPage=_pdf_header_footer, onLaterPages=_pdf_header_footer)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div class="app-hero">
        <h1>☀️ Solar Quotation Generator</h1>
        <p>Create a professional, client-ready solar proposal with guided navigation and a colorful international-standard PDF.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Progress / page navigator
current = st.session_state.current_page
progress = (current + 1) / len(PAGES)
st.progress(progress, text=f"Step {current + 1} of {len(PAGES)} — {PAGES[current][1]} {PAGES[current][0]}")

nav_cols = st.columns(len(PAGES))
for i, (label, icon) in enumerate(PAGES):
    with nav_cols[i]:
        st.button(
            f"{icon} {i + 1}",
            key=key(f"top_page_{i}"),
            use_container_width=True,
            type="primary" if i == current else "secondary",
            on_click=lambda page=i: st.session_state.__setitem__("current_page", page),
        )

st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.caption(f"**Current page:** {PAGES[current][1]} {PAGES[current][0]}")
st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PAGE 1 — COMPANY & CLIENT
# ============================================================

if current == 0:
    st.header("👤 Company & Client")
    st.caption("Enter the commercial and contact information that will appear on the quotation.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Your Company")
        q["company"]["name"] = st.text_input("Company Name", value=q["company"]["name"], key=key("company_name"))
        q["company"]["address"] = st.text_area("Company Address", value=q["company"]["address"], key=key("company_address"))
        q["company"]["phone"] = st.text_input("Phone", value=q["company"]["phone"], key=key("company_phone"))
        q["company"]["email"] = st.text_input("Email", value=q["company"]["email"], key=key("company_email"))
        q["company"]["website"] = st.text_input("Website", value=q["company"]["website"], key=key("company_website"))
        q["company"]["ntn"] = st.text_input("NTN / Registration Number", value=q["company"]["ntn"], key=key("company_ntn"))

    with c2:
        st.subheader("Client")
        q["client"]["name"] = st.text_input("Client Name", value=q["client"]["name"], key=key("client_name"))
        q["client"]["company"] = st.text_input("Client Company", value=q["client"]["company"], key=key("client_company"))
        q["client"]["address"] = st.text_area("Project / Site Address", value=q["client"]["address"], key=key("client_address"))
        q["client"]["phone"] = st.text_input("Client Phone", value=q["client"]["phone"], key=key("client_phone"))
        q["client"]["email"] = st.text_input("Client Email", value=q["client"]["email"], key=key("client_email"))

    d1, d2 = st.columns(2)
    q["quotation_date"] = d1.date_input("Quotation Date", value=q["quotation_date"], key=key("quotation_date"))
    q["quotation_number"] = d2.text_input("Quotation Number", value=q["quotation_number"], key=key("quotation_number"))


# ============================================================
# PAGE 2 — SOLAR SYSTEM
# ============================================================

elif current == 1:
    st.header("☀️ Solar System")
    st.caption("Define the core PV generation, inverter and battery configuration.")

    p = q["panels"]
    st.subheader("Solar Panels")
    c1, c2, c3 = st.columns(3)
    manufacturers = ["LONGi", "Jinko", "JA Solar", "Canadian Solar", "Trina", "Other"]
    p["manufacturer"] = c1.selectbox("Manufacturer", manufacturers, index=manufacturers.index(p["manufacturer"]) if p["manufacturer"] in manufacturers else 0, key=key("panel_manufacturer"))
    p["model"] = c2.text_input("Model", value=p["model"], key=key("panel_model"))
    p["wattage"] = c3.number_input("Wattage (W)", min_value=1.0, value=float(p["wattage"]), step=1.0, key=key("panel_wattage"))
    c1, c2, c3 = st.columns(3)
    p["quantity"] = c1.number_input("Quantity", min_value=1, value=int(p["quantity"]), step=1, key=key("panel_quantity"))
    p["unit_price"] = c2.number_input("Unit Price (PKR)", min_value=0.0, value=float(p["unit_price"]), step=1000.0, key=key("panel_price"))
    p["description"] = c3.text_input("Description", value=p["description"], key=key("panel_description"))

    inv = q["inverter"]
    st.subheader("Inverter")
    inverter_types = ["On-Grid", "Hybrid", "Off-Grid", "All-in-One", "Other"]
    inv["type"] = st.selectbox("Inverter Type", inverter_types, index=inverter_types.index(inv["type"]) if inv["type"] in inverter_types else 0, key=key("inverter_type"))
    c1, c2, c3 = st.columns(3)
    inv["manufacturer"] = c1.text_input("Manufacturer", value=inv["manufacturer"], key=key("inverter_manufacturer"))
    inv["model"] = c2.text_input("Model", value=inv["model"], key=key("inverter_model"))
    inv["capacity_kw"] = c3.number_input("Capacity (kW)", min_value=0.1, value=float(inv["capacity_kw"]), step=0.1, key=key("inverter_capacity"))
    c1, c2 = st.columns(2)
    inv["quantity"] = c1.number_input("Quantity", min_value=1, value=int(inv["quantity"]), step=1, key=key("inverter_quantity"))
    inv["unit_price"] = c2.number_input("Unit Price (PKR)", min_value=0.0, value=float(inv["unit_price"]), step=1000.0, key=key("inverter_price"))

    b = q["battery"]
    st.subheader("Battery")
    battery_required = st.radio("Battery Required?", ["No", "Yes"], index=1 if b["required"] else 0, horizontal=True, key=key("battery_required"))
    b["required"] = battery_required == "Yes"
    if b["required"]:
        battery_types = ["Lithium-ion", "LiFePO4", "Lead Acid", "Tubular", "Gel", "AGM", "Other"]
        c1, c2, c3 = st.columns(3)
        b["type"] = c1.selectbox("Battery Type", battery_types, index=battery_types.index(b["type"]) if b["type"] in battery_types else 0, key=key("battery_type"))
        b["manufacturer"] = c2.text_input("Battery Manufacturer", value=b["manufacturer"], key=key("battery_manufacturer"))
        b["model"] = c3.text_input("Battery Model", value=b["model"], key=key("battery_model"))
        c1, c2, c3 = st.columns(3)
        b["capacity_kwh"] = c1.number_input("Capacity (kWh)", min_value=0.1, value=float(b["capacity_kwh"]), step=0.1, key=key("battery_capacity"))
        b["quantity"] = c2.number_input("Quantity", min_value=1, value=int(b["quantity"]), step=1, key=key("battery_quantity"))
        b["unit_price"] = c3.number_input("Unit Price (PKR)", min_value=0.0, value=float(b["unit_price"]), step=1000.0, key=key("battery_price"))

    calc = calculate_quotation(q)
    m1, m2, m3 = st.columns(3)
    m1.metric("PV Capacity", f"{calc['pv_kwp']:.2f} kWp")
    m2.metric("Inverter Capacity", f"{calc['inverter_kw']:.2f} kW")
    m3.metric("Battery Capacity", f"{calc['battery_kwh']:.2f} kWh" if b["required"] else "N/A")


# ============================================================
# PAGE 3 — ITEMS & SERVICES
# ============================================================

elif current == 2:
    st.header("🧰 Items & Services")
    st.caption("Define the balance-of-system, civil, transportation and installation scope.")

    for item_key, title in [
        ("structure", "Solar Structure"),
        ("cables", "Cables"),
        ("bos", "Protection & Balance of System"),
        ("civil", "Civil Work"),
        ("transportation", "Transportation"),
        ("other", "Other / Miscellaneous"),
    ]:
        item = q[item_key]
        with st.container(border=True):
            st.subheader(title)
            item["included"] = st.checkbox("Include this item", value=item.get("included", True), key=key(f"{item_key}_included"))
            if item["included"]:
                c1, c2, c3 = st.columns(3)
                item["description"] = c1.text_input("Description", value=item.get("description", ""), key=key(f"{item_key}_description"))
                item["quantity"] = c2.number_input("Quantity", min_value=0.0, value=float(item.get("quantity", 1)), key=key(f"{item_key}_quantity"))
                item["unit_price"] = c3.number_input("Unit Price / Lump Sum (PKR)", min_value=0.0, value=float(item.get("unit_price", 0)), step=1000.0, key=key(f"{item_key}_unit_price"))

    st.subheader("Standard Installation")
    q["installation"]["mode"] = st.radio("Installation Cost Method", ["Rate per kWp", "Manual Fixed Cost"], index=0 if q["installation"]["mode"] == "Rate per kWp" else 1, horizontal=True, key=key("installation_mode"))
    if q["installation"]["mode"] == "Rate per kWp":
        q["installation"]["rate_per_kwp"] = st.number_input("Installation Rate (PKR/kWp)", min_value=0.0, value=float(q["installation"]["rate_per_kwp"]), step=500.0, key=key("installation_rate"))
    else:
        q["installation"]["manual_cost"] = st.number_input("Manual Installation Cost (PKR)", min_value=0.0, value=float(q["installation"]["manual_cost"]), step=1000.0, key=key("installation_manual"))


# ============================================================
# PAGE 4 — OPTIONAL ITEMS
# ============================================================

elif current == 3:
    st.header("➕ Optional Items")
    st.caption("Optional services remain outside the Grand Total unless you explicitly include them.")

    for item_key, title in [
        ("metering", "Net Metering / Gross Metering — Complete Job"),
        ("earthing", "Earthing"),
        ("lightning", "Lightning Arrestor"),
    ]:
        item = q["optional"][item_key]
        with st.container(border=True):
            st.subheader(title)
            item["include"] = st.checkbox("Include in Quotation Total?", value=item["include"], key=key(f"optional_{item_key}_include"))
            c1, c2, c3 = st.columns(3)
            if item_key == "metering":
                options = ["Net Metering", "Gross Metering"]
                item["type"] = c1.selectbox("Type", options, index=options.index(item["type"]) if item["type"] in options else 0, key=key("optional_metering_type"))
            elif item_key == "earthing":
                options = ["Complete Earthing", "Equipment Earthing", "Solar Structure Earthing", "Custom Earthing"]
                item["type"] = c1.selectbox("Earthing Type", options, index=options.index(item["type"]) if item["type"] in options else 0, key=key("optional_earthing_type"))
            else:
                options = ["Conventional Lightning Arrestor", "ESE Lightning Arrestor", "Custom"]
                item["type"] = c1.selectbox("Type / Specification", options, index=options.index(item["type"]) if item["type"] in options else 0, key=key("optional_lightning_type"))
            item["quantity"] = c2.number_input("Quantity", min_value=1, value=int(item["quantity"]), step=1, key=key(f"optional_{item_key}_quantity"))
            item["unit_price"] = c3.number_input("Price (PKR)", min_value=0.0, value=float(item["unit_price"]), step=1000.0, key=key(f"optional_{item_key}_price"))
            item["description"] = st.text_area("Description", value=item["description"], key=key(f"optional_{item_key}_description"))
            st.caption("Status: " + ("Included in Grand Total" if item["include"] else "Optional / Not Included"))


# ============================================================
# PAGE 5 — PRICING
# ============================================================

elif current == 4:
    st.header("💰 Pricing")
    st.caption("Review discount, tax and the final project value before generating the quotation.")

    options = ["Percentage", "Fixed PKR"]
    q["discount_type"] = st.radio("Discount Type", options, index=options.index(q["discount_type"]) if q["discount_type"] in options else 0, horizontal=True, key=key("discount_type"))
    if q["discount_type"] == "Percentage":
        q["discount_value"] = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=float(q["discount_value"]), step=0.5, key=key("discount_percentage"))
    else:
        q["discount_value"] = st.number_input("Discount (PKR)", min_value=0.0, value=float(q["discount_value"]), step=1000.0, key=key("discount_fixed"))
    q["tax_rate"] = st.number_input("Tax (%) — enter 0 for no tax", min_value=0.0, max_value=100.0, value=float(q["tax_rate"]), step=0.5, key=key("tax_rate"))

    calc = calculate_quotation(q)
    a, b, c = st.columns(3)
    a.metric("Main Equipment & Services", money(calc["main_subtotal"]))
    b.metric("Included Optional Items", money(calc["included_optional"]))
    c.metric("Subtotal", money(calc["subtotal"]))
    a, b, c = st.columns(3)
    a.metric("Discount", money(calc["discount"]))
    b.metric("Tax", money(calc["tax"]))
    c.metric("GRAND TOTAL", money(calc["grand_total"]))

    st.success(f"Amount in Words: {amount_in_words(calc['grand_total'])}")


# ============================================================
# PAGE 6 — TERMS
# ============================================================

elif current == 5:
    st.header("📋 Terms & Conditions")
    st.caption("These terms are printed in the final quotation. Edit them to match your commercial policy.")
    q["terms"] = st.text_area("Terms & Conditions", value=q["terms"], height=520, key=key("terms"))


# ============================================================
# PAGE 7 — GENERATE
# ============================================================

elif current == 6:
    st.header("📄 Generate Quotation")
    st.caption("Your final quotation will be generated as a polished, colorful, multi-page A4 PDF.")

    calc = calculate_quotation(q)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PV", f"{calc['pv_kwp']:.2f} kWp")
    c2.metric("Inverter", f"{calc['inverter_kw']:.2f} kW")
    c3.metric("Subtotal", money(calc["subtotal"]))
    c4.metric("Grand Total", money(calc["grand_total"]))

    st.markdown("### Final Check")
    checks = [
        ("Company name", bool(q["company"]["name"].strip())),
        ("Client name", bool(q["client"]["name"].strip())),
        ("Quotation number", bool(q["quotation_number"].strip())),
        ("Panel unit price", float(q["panels"]["unit_price"]) > 0),
        ("Inverter unit price", float(q["inverter"]["unit_price"]) > 0),
        ("Terms & conditions", bool(q["terms"].strip())),
    ]
    for label, ok in checks:
        st.write(("✅" if ok else "⚠️") + " " + label)

    st.divider()
    st.markdown("### Ready to Generate")
    if st.button("📄 Generate Professional Quotation PDF", type="primary", use_container_width=True, key=key("generate_pdf")):
        try:
            st.session_state.generated_pdf = generate_international_pdf(q)
            st.success("Quotation generated successfully. Review the PDF below and download it for your client.")
        except Exception as exc:
            st.session_state.generated_pdf = None
            st.error(f"Unable to generate the quotation: {exc}")

    if st.session_state.generated_pdf:
        filename = f"Solar_Quotation_{q['quotation_number'].replace('/', '-')}.pdf"
        st.download_button(
            "⬇️ Download Final Quotation",
            data=st.session_state.generated_pdf,
            file_name=filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key=key("download_pdf"),
        )
        st.info("The PDF includes a branded cover, system summary, detailed commercial schedule, optional services, pricing summary, terms and signature/acceptance section.")


# ============================================================
# BOTTOM NAVIGATION
# ============================================================

st.divider()
nav1, nav2, nav3, nav4 = st.columns([1, 1, 2, 1])
with nav1:
    st.button("← Previous", disabled=current == 0, use_container_width=True, key=key("bottom_previous"), on_click=go_previous)
with nav2:
    st.button("Next →", disabled=current == len(PAGES) - 1, use_container_width=True, key=key("bottom_next"), on_click=go_next)
with nav3:
    st.caption(f"**Step {current + 1}/{len(PAGES)}:** {PAGES[current][1]}")
with nav4:
    st.button("↺ New Quotation", use_container_width=True, key=key("reset"), on_click=reset_quotation)

st.markdown('<div class="footer-note">Solar Quotation Generator • Guided workflow • Professional PDF output</div>', unsafe_allow_html=True)
