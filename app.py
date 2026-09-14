import streamlit as st
from datetime import date
from services.quotation_data import default_quotation
from services.quotation_calculator import (
    calculate_quotation,
    amount_in_words,
)

st.set_page_config(
    page_title="Solar Quotation Generator",
    page_icon="☀️",
    layout="wide",
)

def money(value):
    return f"PKR {value:,.0f}"

if "quotation" not in st.session_state:
    st.session_state.quotation = default_quotation()

q = st.session_state.quotation

st.title("☀️ Solar Quotation Generator")
st.caption("Create professional solar quotations quickly and accurately.")

tabs = st.tabs([
    "Company & Client",
    "Solar System",
    "Items & Services",
    "Optional Items",
    "Pricing",
    "Terms & Conditions",
    "Preview",
])

with tabs[0]:
    st.header("Company Information")
    c1, c2 = st.columns(2)
    with c1:
        q["company"]["name"] = st.text_input("Company Name", q["company"]["name"])
        q["company"]["address"] = st.text_area("Company Address", q["company"]["address"])
        q["company"]["phone"] = st.text_input("Phone", q["company"]["phone"])
        q["company"]["email"] = st.text_input("Email", q["company"]["email"])
    with c2:
        q["company"]["website"] = st.text_input("Website", q["company"]["website"])
        q["company"]["ntn"] = st.text_input("NTN / Registration Number", q["company"]["ntn"])
        q["client"]["name"] = st.text_input("Client Name", q["client"]["name"])
        q["client"]["company"] = st.text_input("Client Company", q["client"]["company"])
        q["client"]["address"] = st.text_area("Client Address / Location", q["client"]["address"])
        q["client"]["phone"] = st.text_input("Client Phone", q["client"]["phone"])
        q["client"]["email"] = st.text_input("Client Email", q["client"]["email"])

    q["quotation_date"] = st.date_input("Quotation Date", q["quotation_date"])
    q["quotation_number"] = st.text_input("Quotation Number", q["quotation_number"])

with tabs[1]:
    st.header("Solar System")
    st.subheader("Solar Panels")
    p = q["panels"]
    c1, c2, c3 = st.columns(3)
    p["manufacturer"] = c1.selectbox(
        "Manufacturer",
        ["LONGi", "Jinko", "JA Solar", "Canadian Solar", "Trina", "Other"],
        index=["LONGi", "Jinko", "JA Solar", "Canadian Solar", "Trina", "Other"].index(p["manufacturer"])
        if p["manufacturer"] in ["LONGi", "Jinko", "JA Solar", "Canadian Solar", "Trina", "Other"] else 0,
    )
    p["model"] = c2.text_input("Model", p["model"])
    p["wattage"] = c3.number_input("Wattage (W)", min_value=1.0, value=float(p["wattage"]), step=1.0)
    c1, c2, c3 = st.columns(3)
    p["quantity"] = c1.number_input("Quantity", min_value=1, value=int(p["quantity"]), step=1)
    p["unit_price"] = c2.number_input("Unit Price (PKR)", min_value=0.0, value=float(p["unit_price"]), step=1000.0)
    p["description"] = c3.text_input("Description", p["description"])

    st.subheader("Inverter")
    inv = q["inverter"]
    inv["type"] = st.selectbox("Inverter Type", ["On-Grid", "Hybrid", "Off-Grid", "All-in-One", "Other"])
    c1, c2, c3 = st.columns(3)
    inv["manufacturer"] = c1.text_input("Manufacturer", inv["manufacturer"])
    inv["model"] = c2.text_input(
    "Model",
    inv["model"],
    key="inverter_model"
)
    inv["capacity_kw"] = c3.number_input("Capacity (kW)", min_value=0.1, value=float(inv["capacity_kw"]), step=0.1)
    c1, c2 = st.columns(2)
    inv["quantity"] = c1.number_input("Quantity", min_value=1, value=int(inv["quantity"]), step=1)
    inv["unit_price"] = c2.number_input("Unit Price (PKR)", min_value=0.0, value=float(inv["unit_price"]), step=1000.0)

    st.subheader("Battery")
    b = q["battery"]
    b["required"] = st.radio("Battery Required?", ["No", "Yes"], index=1 if b["required"] else 0, horizontal=True) == "Yes"
    if b["required"]:
        c1, c2, c3 = st.columns(3)
        b["type"] = c1.selectbox("Battery Type", ["Lithium-ion", "LiFePO4", "Lead Acid", "Tubular", "Gel", "AGM", "Other"])
        b["manufacturer"] = c2.text_input("Battery Manufacturer", b["manufacturer"])
        b["model"] = c3.text_input("Battery Model", b["model"])
        c1, c2, c3 = st.columns(3)
        b["capacity_kwh"] = c1.number_input("Capacity (kWh)", min_value=0.1, value=float(b["capacity_kwh"]), step=0.1)
        b["quantity"] = c2.number_input("Quantity", min_value=1, value=int(b["quantity"]), step=1)
        b["unit_price"] = c3.number_input("Unit Price (PKR)", min_value=0.0, value=float(b["unit_price"]), step=1000.0)

    calc = calculate_quotation(q)
    m1, m2, m3 = st.columns(3)
    m1.metric("PV Capacity", f'{calc["pv_kwp"]:.2f} kWp')
    m2.metric("Inverter Capacity", f'{calc["inverter_kw"]:.2f} kW')
    m3.metric("Battery Capacity", f'{calc["battery_kwh"]:.2f} kWh' if b["required"] else "N/A")

with tabs[2]:
    st.header("Items & Services")
    st.info("The MVP uses simple single-entry sections. Additional item rows can be added in later iterations.")
    for key, title in [
        ("structure", "Solar Structure"),
        ("cables", "Cables"),
        ("bos", "Protection & Balance of System"),
        ("civil", "Civil Work"),
        ("transportation", "Transportation"),
        ("other", "Other / Miscellaneous"),
    ]:
        item = q[key]
        st.subheader(title)
        item["included"] = st.checkbox("Included", value=item.get("included", True), key=f"{key}_included")
        if item["included"]:
            c1, c2, c3 = st.columns(3)
            item["description"] = c1.text_input("Description", item.get("description", ""), key=f"{key}_desc")
            item["quantity"] = c2.number_input("Quantity", min_value=0.0, value=float(item.get("quantity", 1)), key=f"{key}_qty")
            item["unit_price"] = c3.number_input("Unit Price / Lump Sum (PKR)", min_value=0.0, value=float(item.get("unit_price", 0)), step=1000.0, key=f"{key}_price")

    st.subheader("Standard Installation")
    q["installation"]["mode"] = st.radio(
        "Installation Cost Method",
        ["Rate per kWp", "Manual Fixed Cost"],
        index=0 if q["installation"]["mode"] == "Rate per kWp" else 1,
        horizontal=True,
    )
    if q["installation"]["mode"] == "Rate per kWp":
        q["installation"]["rate_per_kwp"] = st.number_input(
            "Installation Rate (PKR/kWp)",
            min_value=0.0,
            value=float(q["installation"]["rate_per_kwp"]),
            step=500.0,
        )
    else:
        q["installation"]["manual_cost"] = st.number_input(
            "Manual Installation Cost (PKR)",
            min_value=0.0,
            value=float(q["installation"]["manual_cost"]),
            step=1000.0,
        )

with tabs[3]:
    st.header("OPTIONAL ITEMS")
    st.caption("Optional items are excluded from the Grand Total unless 'Include in Quotation Total' is selected.")

    for key, title in [
        ("metering", "Net Metering / Gross Metering — Complete Job"),
        ("earthing", "Earthing"),
        ("lightning", "Lightning Arrestor"),
    ]:
        item = q["optional"][key]
        st.subheader(title)
        item["include"] = st.checkbox("Include in Quotation Total?", value=item["include"], key=f"opt_{key}_include")
        c1, c2, c3 = st.columns(3)
        if key == "metering":
            item["type"] = c1.selectbox("Type", ["Net Metering", "Gross Metering"], key="metering_type")
        elif key == "earthing":
            item["type"] = c1.selectbox("Earthing Type", ["Complete Earthing", "Equipment Earthing", "Solar Structure Earthing", "Custom Earthing"], key="earthing_type")
        else:
            item["type"] = c1.selectbox("Type / Specification", ["Conventional Lightning Arrestor", "ESE Lightning Arrestor", "Custom"], key="lightning_type")
        item["quantity"] = c2.number_input("Quantity", min_value=1, value=int(item["quantity"]), step=1, key=f"opt_{key}_qty")
        item["unit_price"] = c3.number_input("Price (PKR)", min_value=0.0, value=float(item["unit_price"]), step=1000.0, key=f"opt_{key}_price")
        item["description"] = st.text_area("Description", item["description"], key=f"opt_{key}_desc")
        st.caption("Status: " + ("Included" if item["include"] else "Optional / Not Included"))

with tabs[4]:
    st.header("Pricing Summary")
    q["discount_type"] = st.radio("Discount Type", ["Percentage", "Fixed PKR"], horizontal=True)
    if q["discount_type"] == "Percentage":
        q["discount_value"] = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=float(q["discount_value"]), step=0.5)
    else:
        q["discount_value"] = st.number_input("Discount (PKR)", min_value=0.0, value=float(q["discount_value"]), step=1000.0)

    q["tax_rate"] = st.number_input("Tax (%) — enter 0 for no tax", min_value=0.0, max_value=100.0, value=float(q["tax_rate"]), step=0.5)

    calc = calculate_quotation(q)
    st.metric("Main Equipment & Services", money(calc["main_subtotal"]))
    st.metric("Included Optional Items", money(calc["included_optional"]))
    st.metric("Subtotal Before Discount/Tax", money(calc["subtotal"]))
    st.metric("Discount", money(calc["discount"]))
    st.metric("Tax", money(calc["tax"]))
    st.metric("GRAND TOTAL", money(calc["grand_total"]))
    st.success(f'Amount in Words: {amount_in_words(calc["grand_total"])}')

with tabs[5]:
    st.header("Terms & Conditions")
    q["terms"] = st.text_area(
        "Edit Terms & Conditions",
        q["terms"],
        height=500,
        help="These terms are fully editable and will appear in the final quotation PDF.",
    )

with tabs[6]:
    st.header("Quotation Preview")
    calc = calculate_quotation(q)
    st.subheader("Quotation")
    st.write(f"**Quotation No.:** {q['quotation_number']}  |  **Date:** {q['quotation_date']}")
    st.write(f"**Client:** {q['client']['name'] or 'Not entered'}")
    st.write(f"**PV System:** {calc['pv_kwp']:.2f} kWp")
    st.write(f"**Inverter Capacity:** {calc['inverter_kw']:.2f} kW")
    if q["battery"]["required"]:
        st.write(f"**Battery Capacity:** {calc['battery_kwh']:.2f} kWh")
    st.divider()
    st.write(f"**Grand Total: {money(calc['grand_total'])}**")
    st.write(f"**Amount in Words:** {amount_in_words(calc['grand_total'])}")
    st.subheader("Optional Items")
    for item in q["optional"].values():
        st.write(f"- {item['type']}: {money(item['quantity'] * item['unit_price'])} — {'Included' if item['include'] else 'Optional / Not Included'}")
    st.subheader("Terms & Conditions")
    st.text(q["terms"])

st.sidebar.header("Quotation Controls")
if st.sidebar.button("Reset Quotation"):
    st.session_state.quotation = default_quotation()
    st.rerun()

st.sidebar.info("MVP calculation engine is deterministic Python. No AI/API is used for financial calculations.")
