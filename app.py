import streamlit as st
from datetime import date

from services.quotation_data import default_quotation
from services.quotation_calculator import (
    calculate_quotation,
    amount_in_words,
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Solar Quotation Generator",
    page_icon="☀️",
    layout="wide",
)

# ============================================================
# HELPERS
# ============================================================

def money(value):
    return f"PKR {value:,.0f}"


def widget_key(name):
    """
    Give every Streamlit widget a unique, stable key.

    The version prefix is changed when the quotation is reset so
    Streamlit does not reuse old widget state after a reset.
    """
    return f"quotation_v{st.session_state.widget_version}_{name}"


# ============================================================
# SESSION STATE
# ============================================================

if "quotation" not in st.session_state:
    st.session_state.quotation = default_quotation()

if "widget_version" not in st.session_state:
    st.session_state.widget_version = 0


def reset_quotation():
    st.session_state.quotation = default_quotation()
    st.session_state.widget_version += 1


q = st.session_state.quotation

# ============================================================
# HEADER
# ============================================================

st.title("☀️ Solar Quotation Generator")
st.caption("Create professional solar quotations quickly and accurately.")

tabs = st.tabs(
    [
        "Company & Client",
        "Solar System",
        "Items & Services",
        "Optional Items",
        "Pricing",
        "Terms & Conditions",
        "Preview",
    ]
)

# ============================================================
# COMPANY & CLIENT
# ============================================================

with tabs[0]:
    st.header("Company Information")

    c1, c2 = st.columns(2)

    with c1:
        q["company"]["name"] = st.text_input(
            "Company Name",
            value=q["company"]["name"],
            key=widget_key("company_name"),
        )
        q["company"]["address"] = st.text_area(
            "Company Address",
            value=q["company"]["address"],
            key=widget_key("company_address"),
        )
        q["company"]["phone"] = st.text_input(
            "Phone",
            value=q["company"]["phone"],
            key=widget_key("company_phone"),
        )
        q["company"]["email"] = st.text_input(
            "Email",
            value=q["company"]["email"],
            key=widget_key("company_email"),
        )

    with c2:
        q["company"]["website"] = st.text_input(
            "Website",
            value=q["company"]["website"],
            key=widget_key("company_website"),
        )
        q["company"]["ntn"] = st.text_input(
            "NTN / Registration Number",
            value=q["company"]["ntn"],
            key=widget_key("company_ntn"),
        )
        q["client"]["name"] = st.text_input(
            "Client Name",
            value=q["client"]["name"],
            key=widget_key("client_name"),
        )
        q["client"]["company"] = st.text_input(
            "Client Company",
            value=q["client"]["company"],
            key=widget_key("client_company"),
        )
        q["client"]["address"] = st.text_area(
            "Client Address / Location",
            value=q["client"]["address"],
            key=widget_key("client_address"),
        )
        q["client"]["phone"] = st.text_input(
            "Client Phone",
            value=q["client"]["phone"],
            key=widget_key("client_phone"),
        )
        q["client"]["email"] = st.text_input(
            "Client Email",
            value=q["client"]["email"],
            key=widget_key("client_email"),
        )

    q["quotation_date"] = st.date_input(
        "Quotation Date",
        value=q["quotation_date"],
        key=widget_key("quotation_date"),
    )
    q["quotation_number"] = st.text_input(
        "Quotation Number",
        value=q["quotation_number"],
        key=widget_key("quotation_number"),
    )

# ============================================================
# SOLAR SYSTEM
# ============================================================

with tabs[1]:
    st.header("Solar System")

    # ----------------------------
    # Solar Panels
    # ----------------------------

    st.subheader("Solar Panels")
    p = q["panels"]

    manufacturers = [
        "LONGi",
        "Jinko",
        "JA Solar",
        "Canadian Solar",
        "Trina",
        "Other",
    ]

    c1, c2, c3 = st.columns(3)

    p["manufacturer"] = c1.selectbox(
        "Manufacturer",
        manufacturers,
        index=(
            manufacturers.index(p["manufacturer"])
            if p["manufacturer"] in manufacturers
            else 0
        ),
        key=widget_key("panels_manufacturer"),
    )

    p["model"] = c2.text_input(
        "Model",
        value=p["model"],
        key=widget_key("panels_model"),
    )

    p["wattage"] = c3.number_input(
        "Wattage (W)",
        min_value=1.0,
        value=float(p["wattage"]),
        step=1.0,
        key=widget_key("panels_wattage"),
    )

    c1, c2, c3 = st.columns(3)

    p["quantity"] = c1.number_input(
        "Quantity",
        min_value=1,
        value=int(p["quantity"]),
        step=1,
        key=widget_key("panels_quantity"),
    )

    p["unit_price"] = c2.number_input(
        "Unit Price (PKR)",
        min_value=0.0,
        value=float(p["unit_price"]),
        step=1000.0,
        key=widget_key("panels_unit_price"),
    )

    p["description"] = c3.text_input(
        "Description",
        value=p["description"],
        key=widget_key("panels_description"),
    )

    # ----------------------------
    # Inverter
    # ----------------------------

    st.subheader("Inverter")
    inv = q["inverter"]

    inverter_types = [
        "On-Grid",
        "Hybrid",
        "Off-Grid",
        "All-in-One",
        "Other",
    ]

    inv["type"] = st.selectbox(
        "Inverter Type",
        inverter_types,
        index=(
            inverter_types.index(inv["type"])
            if inv["type"] in inverter_types
            else 0
        ),
        key=widget_key("inverter_type"),
    )

    c1, c2, c3 = st.columns(3)

    inv["manufacturer"] = c1.text_input(
        "Manufacturer",
        value=inv["manufacturer"],
        key=widget_key("inverter_manufacturer"),
    )

    inv["model"] = c2.text_input(
        "Model",
        value=inv["model"],
        key=widget_key("inverter_model"),
    )

    inv["capacity_kw"] = c3.number_input(
        "Capacity (kW)",
        min_value=0.1,
        value=float(inv["capacity_kw"]),
        step=0.1,
        key=widget_key("inverter_capacity_kw"),
    )

    c1, c2 = st.columns(2)

    inv["quantity"] = c1.number_input(
        "Quantity",
        min_value=1,
        value=int(inv["quantity"]),
        step=1,
        key=widget_key("inverter_quantity"),
    )

    inv["unit_price"] = c2.number_input(
        "Unit Price (PKR)",
        min_value=0.0,
        value=float(inv["unit_price"]),
        step=1000.0,
        key=widget_key("inverter_unit_price"),
    )

    # ----------------------------
    # Battery
    # ----------------------------

    st.subheader("Battery")
    b = q["battery"]

    battery_required_options = ["No", "Yes"]

    battery_required = st.radio(
        "Battery Required?",
        battery_required_options,
        index=1 if b["required"] else 0,
        horizontal=True,
        key=widget_key("battery_required"),
    )
    b["required"] = battery_required == "Yes"

    if b["required"]:
        battery_types = [
            "Lithium-ion",
            "LiFePO4",
            "Lead Acid",
            "Tubular",
            "Gel",
            "AGM",
            "Other",
        ]

        c1, c2, c3 = st.columns(3)

        b["type"] = c1.selectbox(
            "Battery Type",
            battery_types,
            index=(
                battery_types.index(b["type"])
                if b["type"] in battery_types
                else 0
            ),
            key=widget_key("battery_type"),
        )

        b["manufacturer"] = c2.text_input(
            "Battery Manufacturer",
            value=b["manufacturer"],
            key=widget_key("battery_manufacturer"),
        )

        b["model"] = c3.text_input(
            "Battery Model",
            value=b["model"],
            key=widget_key("battery_model"),
        )

        c1, c2, c3 = st.columns(3)

        b["capacity_kwh"] = c1.number_input(
            "Capacity (kWh)",
            min_value=0.1,
            value=float(b["capacity_kwh"]),
            step=0.1,
            key=widget_key("battery_capacity_kwh"),
        )

        b["quantity"] = c2.number_input(
            "Quantity",
            min_value=1,
            value=int(b["quantity"]),
            step=1,
            key=widget_key("battery_quantity"),
        )

        b["unit_price"] = c3.number_input(
            "Unit Price (PKR)",
            min_value=0.0,
            value=float(b["unit_price"]),
            step=1000.0,
            key=widget_key("battery_unit_price"),
        )

    calc = calculate_quotation(q)

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "PV Capacity",
        f'{calc["pv_kwp"]:.2f} kWp',
    )

    m2.metric(
        "Inverter Capacity",
        f'{calc["inverter_kw"]:.2f} kW',
    )

    m3.metric(
        "Battery Capacity",
        (
            f'{calc["battery_kwh"]:.2f} kWh'
            if b["required"]
            else "N/A"
        ),
    )

# ============================================================
# ITEMS & SERVICES
# ============================================================

with tabs[2]:
    st.header("Items & Services")
    st.info(
        "The MVP uses simple single-entry sections. "
        "Additional item rows can be added in later iterations."
    )

    service_items = [
        ("structure", "Solar Structure"),
        ("cables", "Cables"),
        ("bos", "Protection & Balance of System"),
        ("civil", "Civil Work"),
        ("transportation", "Transportation"),
        ("other", "Other / Miscellaneous"),
    ]

    for item_key, title in service_items:
        item = q[item_key]

        st.subheader(title)

        item["included"] = st.checkbox(
            "Included",
            value=item.get("included", True),
            key=widget_key(f"{item_key}_included"),
        )

        if item["included"]:
            c1, c2, c3 = st.columns(3)

            item["description"] = c1.text_input(
                "Description",
                value=item.get("description", ""),
                key=widget_key(f"{item_key}_description"),
            )

            item["quantity"] = c2.number_input(
                "Quantity",
                min_value=0.0,
                value=float(item.get("quantity", 1)),
                key=widget_key(f"{item_key}_quantity"),
            )

            item["unit_price"] = c3.number_input(
                "Unit Price / Lump Sum (PKR)",
                min_value=0.0,
                value=float(item.get("unit_price", 0)),
                step=1000.0,
                key=widget_key(f"{item_key}_unit_price"),
            )

    st.subheader("Standard Installation")

    installation_modes = [
        "Rate per kWp",
        "Manual Fixed Cost",
    ]

    q["installation"]["mode"] = st.radio(
        "Installation Cost Method",
        installation_modes,
        index=(
            0
            if q["installation"]["mode"] == "Rate per kWp"
            else 1
        ),
        horizontal=True,
        key=widget_key("installation_mode"),
    )

    if q["installation"]["mode"] == "Rate per kWp":
        q["installation"]["rate_per_kwp"] = st.number_input(
            "Installation Rate (PKR/kWp)",
            min_value=0.0,
            value=float(q["installation"]["rate_per_kwp"]),
            step=500.0,
            key=widget_key("installation_rate_per_kwp"),
        )
    else:
        q["installation"]["manual_cost"] = st.number_input(
            "Manual Installation Cost (PKR)",
            min_value=0.0,
            value=float(q["installation"]["manual_cost"]),
            step=1000.0,
            key=widget_key("installation_manual_cost"),
        )

# ============================================================
# OPTIONAL ITEMS
# ============================================================

with tabs[3]:
    st.header("OPTIONAL ITEMS")
    st.caption(
        "Optional items are excluded from the Grand Total unless "
        "'Include in Quotation Total' is selected."
    )

    optional_items = [
        (
            "metering",
            "Net Metering / Gross Metering — Complete Job",
        ),
        ("earthing", "Earthing"),
        ("lightning", "Lightning Arrestor"),
    ]

    for item_key, title in optional_items:
        item = q["optional"][item_key]

        st.subheader(title)

        item["include"] = st.checkbox(
            "Include in Quotation Total?",
            value=item["include"],
            key=widget_key(f"optional_{item_key}_include"),
        )

        c1, c2, c3 = st.columns(3)

        if item_key == "metering":
            metering_types = [
                "Net Metering",
                "Gross Metering",
            ]
            item["type"] = c1.selectbox(
                "Type",
                metering_types,
                index=(
                    metering_types.index(item["type"])
                    if item["type"] in metering_types
                    else 0
                ),
                key=widget_key("optional_metering_type"),
            )

        elif item_key == "earthing":
            earthing_types = [
                "Complete Earthing",
                "Equipment Earthing",
                "Solar Structure Earthing",
                "Custom Earthing",
            ]
            item["type"] = c1.selectbox(
                "Earthing Type",
                earthing_types,
                index=(
                    earthing_types.index(item["type"])
                    if item["type"] in earthing_types
                    else 0
                ),
                key=widget_key("optional_earthing_type"),
            )

        else:
            lightning_types = [
                "Conventional Lightning Arrestor",
                "ESE Lightning Arrestor",
                "Custom",
            ]
            item["type"] = c1.selectbox(
                "Type / Specification",
                lightning_types,
                index=(
                    lightning_types.index(item["type"])
                    if item["type"] in lightning_types
                    else 0
                ),
                key=widget_key("optional_lightning_type"),
            )

        item["quantity"] = c2.number_input(
            "Quantity",
            min_value=1,
            value=int(item["quantity"]),
            step=1,
            key=widget_key(f"optional_{item_key}_quantity"),
        )

        item["unit_price"] = c3.number_input(
            "Price (PKR)",
            min_value=0.0,
            value=float(item["unit_price"]),
            step=1000.0,
            key=widget_key(f"optional_{item_key}_unit_price"),
        )

        item["description"] = st.text_area(
            "Description",
            value=item["description"],
            key=widget_key(f"optional_{item_key}_description"),
        )

        st.caption(
            "Status: "
            + ("Included" if item["include"] else "Optional / Not Included")
        )

# ============================================================
# PRICING
# ============================================================

with tabs[4]:
    st.header("Pricing Summary")

    discount_types = [
        "Percentage",
        "Fixed PKR",
    ]

    q["discount_type"] = st.radio(
        "Discount Type",
        discount_types,
        index=(
            discount_types.index(q["discount_type"])
            if q["discount_type"] in discount_types
            else 0
        ),
        horizontal=True,
        key=widget_key("discount_type"),
    )

    if q["discount_type"] == "Percentage":
        q["discount_value"] = st.number_input(
            "Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(q["discount_value"]),
            step=0.5,
            key=widget_key("discount_percentage"),
        )
    else:
        q["discount_value"] = st.number_input(
            "Discount (PKR)",
            min_value=0.0,
            value=float(q["discount_value"]),
            step=1000.0,
            key=widget_key("discount_fixed"),
        )

    q["tax_rate"] = st.number_input(
        "Tax (%) — enter 0 for no tax",
        min_value=0.0,
        max_value=100.0,
        value=float(q["tax_rate"]),
        step=0.5,
        key=widget_key("tax_rate"),
    )

    calc = calculate_quotation(q)

    st.metric(
        "Main Equipment & Services",
        money(calc["main_subtotal"]),
    )
    st.metric(
        "Included Optional Items",
        money(calc["included_optional"]),
    )
    st.metric(
        "Subtotal Before Discount/Tax",
        money(calc["subtotal"]),
    )
    st.metric(
        "Discount",
        money(calc["discount"]),
    )
    st.metric(
        "Tax",
        money(calc["tax"]),
    )
    st.metric(
        "GRAND TOTAL",
        money(calc["grand_total"]),
    )

    st.success(
        f'Amount in Words: {amount_in_words(calc["grand_total"])}'
    )

# ============================================================
# TERMS & CONDITIONS
# ============================================================

with tabs[5]:
    st.header("Terms & Conditions")

    q["terms"] = st.text_area(
        "Edit Terms & Conditions",
        value=q["terms"],
        height=500,
        help=(
            "These terms are fully editable and will appear "
            "in the final quotation PDF."
        ),
        key=widget_key("terms"),
    )

# ============================================================
# PREVIEW
# ============================================================

with tabs[6]:
    st.header("Quotation Preview")

    calc = calculate_quotation(q)

    st.subheader("Quotation")

    st.write(
        f"**Quotation No.:** {q['quotation_number']}  |  "
        f"**Date:** {q['quotation_date']}"
    )

    st.write(
        f"**Client:** {q['client']['name'] or 'Not entered'}"
    )

    st.write(
        f"**PV System:** {calc['pv_kwp']:.2f} kWp"
    )

    st.write(
        f"**Inverter Capacity:** {calc['inverter_kw']:.2f} kW"
    )

    if q["battery"]["required"]:
        st.write(
            f"**Battery Capacity:** "
            f"{calc['battery_kwh']:.2f} kWh"
        )

    st.divider()

    st.write(
        f"**Grand Total: {money(calc['grand_total'])}**"
    )

    st.write(
        f"**Amount in Words:** "
        f"{amount_in_words(calc['grand_total'])}"
    )

    st.subheader("Optional Items")

    for item in q["optional"].values():
        status = (
            "Included"
            if item["include"]
            else "Optional / Not Included"
        )

        st.write(
            f"- {item['type']}: "
            f"{money(item['quantity'] * item['unit_price'])} "
            f"— {status}"
        )

    st.subheader("Terms & Conditions")
    st.text(q["terms"])

# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("Quotation Controls")

st.sidebar.button(
    "Reset Quotation",
    on_click=reset_quotation,
    key=widget_key("reset_quotation"),
)

st.sidebar.info(
    "MVP calculation engine is deterministic Python. "
    "No AI/API is used for financial calculations."
)
