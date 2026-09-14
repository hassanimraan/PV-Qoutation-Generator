def _item_total(item):
    if not item.get("included", True):
        return 0.0
    return float(item.get("quantity", 0)) * float(item.get("unit_price", 0))

def calculate_quotation(q):
    panels = q["panels"]
    inverter = q["inverter"]
    battery = q["battery"]

    pv_kwp = float(panels["quantity"]) * float(panels["wattage"]) / 1000
    inverter_kw = float(inverter["quantity"]) * float(inverter["capacity_kw"])
    battery_kwh = (
        float(battery["quantity"]) * float(battery["capacity_kwh"])
        if battery["required"] else 0.0
    )

    main_subtotal = (
        float(panels["quantity"]) * float(panels["unit_price"])
        + float(inverter["quantity"]) * float(inverter["unit_price"])
        + (float(battery["quantity"]) * float(battery["unit_price"]) if battery["required"] else 0.0)
    )

    for key in ["structure", "cables", "bos", "civil", "transportation", "other"]:
        main_subtotal += _item_total(q[key])

    if q["installation"]["mode"] == "Rate per kWp":
        installation_cost = pv_kwp * float(q["installation"]["rate_per_kwp"])
    else:
        installation_cost = float(q["installation"]["manual_cost"])

    main_subtotal += installation_cost

    included_optional = sum(
        float(item["quantity"]) * float(item["unit_price"])
        for item in q["optional"].values()
        if item["include"]
    )

    subtotal = main_subtotal + included_optional

    if q["discount_type"] == "Percentage":
        discount = subtotal * float(q["discount_value"]) / 100
    else:
        discount = float(q["discount_value"])

    after_discount = max(0.0, subtotal - discount)
    tax = after_discount * float(q["tax_rate"]) / 100
    grand_total = after_discount + tax

    return {
        "pv_kwp": pv_kwp,
        "inverter_kw": inverter_kw,
        "battery_kwh": battery_kwh,
        "installation_cost": installation_cost,
        "main_subtotal": main_subtotal,
        "included_optional": included_optional,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "grand_total": grand_total,
    }

ONES = [
    "Zero", "One", "Two", "Three", "Four", "Five",
    "Six", "Seven", "Eight", "Nine", "Ten", "Eleven",
    "Twelve", "Thirteen", "Fourteen", "Fifteen",
    "Sixteen", "Seventeen", "Eighteen", "Nineteen",
]
TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty",
    "Sixty", "Seventy", "Eighty", "Ninety",
]

def _under_thousand(n):
    words = []
    if n >= 100:
        words.append(ONES[n // 100] + " Hundred")
        n %= 100
    if n >= 20:
        words.append(TENS[n // 10])
        n %= 10
    if n:
        words.append(ONES[n])
    return " ".join(words)

def _number_to_words(n):
    if n == 0:
        return "Zero"
    parts = []
    crore = n // 10_000_000
    n %= 10_000_000
    lakh = n // 100_000
    n %= 100_000
    thousand = n // 1_000
    n %= 1_000
    if crore:
        parts.append(_under_thousand(crore) + " Crore")
    if lakh:
        parts.append(_under_thousand(lakh) + " Lakh")
    if thousand:
        parts.append(_under_thousand(thousand) + " Thousand")
    if n:
        parts.append(_under_thousand(n))
    return " ".join(parts)

def amount_in_words(amount):
    rupees = int(round(float(amount)))
    return f"Pakistani Rupees {_number_to_words(rupees)} Only."
