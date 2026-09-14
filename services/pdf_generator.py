from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from services.quotation_calculator import calculate_quotation, amount_in_words

def generate_pdf(q):
    calc = calculate_quotation(q)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12*mm,
        leftMargin=12*mm,
        topMargin=12*mm,
        bottomMargin=12*mm,
        title=f"Quotation {q['quotation_number']}",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=18))
    styles.add(ParagraphStyle(name="RightSmall", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=8))

    story = []

    company = q["company"]
    client = q["client"]

    story.append(Paragraph(company["name"] or "SOLAR COMPANY", styles["CenterTitle"]))
    header_lines = [company["address"], company["phone"], company["email"], company["website"]]
    header_lines = [x for x in header_lines if x]
    if header_lines:
        story.append(Paragraph("<br/>".join(header_lines), styles["Normal"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("QUOTATION", styles["CenterTitle"]))

    meta = [
        ["Quotation No.", q["quotation_number"], "Date", str(q["quotation_date"])],
        ["Client", client["name"], "Client Company", client["company"]],
        ["Address", client["address"], "Phone", client["phone"]],
    ]
    table = Table(meta, colWidths=[28*mm, 65*mm, 32*mm, 53*mm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
        ("BACKGROUND", (2,0), (2,-1), colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 8))

    summary = [
        ["System Summary", "Value"],
        ["PV Capacity", f"{calc['pv_kwp']:.2f} kWp"],
        ["Inverter Capacity", f"{calc['inverter_kw']:.2f} kW"],
    ]
    if q["battery"]["required"]:
        summary.append(["Battery Capacity", f"{calc['battery_kwh']:.2f} kWh"])
    st = Table(summary, colWidths=[70*mm, 45*mm])
    st.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    story.append(st)
    story.append(Spacer(1, 8))

    rows = [["Sr.", "Category", "Description", "Qty", "Unit Price (PKR)", "Total (PKR)"]]
    sr = 1

    def add_row(category, description, qty, price):
        nonlocal sr
        total = qty * price
        rows.append([sr, category, description, f"{qty:g}", f"{price:,.0f}", f"{total:,.0f}"])
        sr += 1

    add_row("Solar Panels", f"{q['panels']['manufacturer']} {q['panels']['model']} — {q['panels']['wattage']:g} W", q["panels"]["quantity"], q["panels"]["unit_price"])
    add_row("Inverter", f"{q['inverter']['manufacturer']} {q['inverter']['model']} — {q['inverter']['capacity_kw']:g} kW", q["inverter"]["quantity"], q["inverter"]["unit_price"])

    if q["battery"]["required"]:
        add_row("Battery", f"{q['battery']['manufacturer']} {q['battery']['model']} — {q['battery']['capacity_kwh']:g} kWh", q["battery"]["quantity"], q["battery"]["unit_price"])

    for key, label in [
        ("structure", "Structure"),
        ("cables", "Cables"),
        ("bos", "Protection & BOS"),
        ("civil", "Civil Work"),
        ("transportation", "Transportation"),
        ("other", "Other Items"),
    ]:
        item = q[key]
        if item.get("included"):
            add_row(label, item["description"], item["quantity"], item["unit_price"])

    add_row("Installation", "Standard Installation", 1, calc["installation_cost"])

    qt = Table(rows, colWidths=[10*mm, 27*mm, 75*mm, 15*mm, 30*mm, 30*mm], repeatRows=1)
    qt.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (3,1), (-1,-1), "RIGHT"),
    ]))
    story.append(qt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("OPTIONAL ITEMS", styles["Heading2"]))
    opt_rows = [["Item", "Description", "Qty", "Price (PKR)", "Status"]]
    for item in q["optional"].values():
        status = "Included" if item["include"] else "Optional / Not Included"
        opt_rows.append([
            item["type"], item["description"], str(item["quantity"]),
            f"{item['unit_price']:,.0f}", status
        ])
    ot = Table(opt_rows, colWidths=[35*mm, 80*mm, 15*mm, 30*mm, 30*mm], repeatRows=1)
    ot.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(ot)
    story.append(Spacer(1, 8))

    totals = [
        ["Main Equipment & Services", f"PKR {calc['main_subtotal']:,.0f}"],
        ["Included Optional Items", f"PKR {calc['included_optional']:,.0f}"],
        ["Subtotal", f"PKR {calc['subtotal']:,.0f}"],
        ["Discount", f"PKR {calc['discount']:,.0f}"],
        ["Tax", f"PKR {calc['tax']:,.0f}"],
        ["GRAND TOTAL", f"PKR {calc['grand_total']:,.0f}"],
    ]
    tt = Table(totals, colWidths=[120*mm, 50*mm])
    tt.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
    ]))
    story.append(tt)
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Amount in Words:</b> {amount_in_words(calc['grand_total'])}", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("TERMS & CONDITIONS", styles["Heading2"]))
    for line in q["terms"].splitlines():
        if line.strip():
            story.append(Paragraph(line.replace("&", "&amp;"), styles["Normal"]))
            story.append(Spacer(1, 2))

    story.append(Spacer(1, 18))
    sig = Table([["Customer Acceptance", "For Company"], ["", ""], ["Name / Signature", "Authorized Signature"]], colWidths=[85*mm, 85*mm], rowHeights=[8*mm, 20*mm, 8*mm])
    sig.setStyle(TableStyle([
        ("LINEBELOW", (0,1), (0,1), 0.5, colors.black),
        ("LINEBELOW", (1,1), (1,1), 0.5, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    story.append(sig)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
