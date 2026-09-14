from datetime import date

DEFAULT_TERMS = """PAYMENT TERMS
• Advance on signing / accepting agreement: 85%
• Upon delivery of material to the site (as mentioned above): 10%
• After installation and commissioning/testing: 5%
• In case of Unforeseen/Force majeure, Contingencies will be paid (if required) as per actual.
• All costs are exclusive of taxes/duties.

GENERAL TERMS AND CONDITIONS
• Please note that these are all A-Quality items quoted.
• Order will be confirmed on receipt of advance payment.
• Prices are exclusive of Transportation costs unless mentioned separately.
• Installation material & labour charges are included in the above estimate.
• Installation will begin in 10 days with response to each payment as per schedule.
• Bidirectional meter installation will take minimum 30 days as per LESCO processing time.
• Grid Sharing Charges for Bidirectional meter (if applicable) will be charged to the client.
• Additional Electrical works, if any, are excluded from the quoted prices.
• Additional Civil works besides foundation, if any, are excluded from the quoted prices.
• After one month of project completion, visitation and servicing will be charged.
• Generator syncing charges: Rs. 350,000/- will be charged separately.
• In case of Extension of Load (EoL), additional AC wire required would be client's responsibility.

NOTE
This quotation is valid for (02) days only due to price fluctuations.
"""

def default_quotation():
    return {
        "company": {
            "name": "",
            "address": "",
            "phone": "",
            "email": "",
            "website": "",
            "ntn": "",
        },
        "client": {
            "name": "",
            "company": "",
            "address": "",
            "phone": "",
            "email": "",
        },
        "quotation_date": date.today(),
        "quotation_number": f"QT-{date.today().year}-001",
        "panels": {
            "manufacturer": "LONGi",
            "model": "",
            "wattage": 645.0,
            "quantity": 1,
            "unit_price": 0.0,
            "description": "Solar PV Module",
        },
        "inverter": {
            "type": "On-Grid",
            "manufacturer": "",
            "model": "",
            "capacity_kw": 10.0,
            "quantity": 1,
            "unit_price": 0.0,
        },
        "battery": {
            "required": False,
            "type": "LiFePO4",
            "manufacturer": "",
            "model": "",
            "capacity_kwh": 10.0,
            "quantity": 1,
            "unit_price": 0.0,
        },
        "structure": {
            "included": True,
            "description": "Solar PV mounting structure",
            "quantity": 1.0,
            "unit_price": 0.0,
        },
        "cables": {
            "included": True,
            "description": "AC/DC cables and accessories",
            "quantity": 1.0,
            "unit_price": 0.0,
        },
        "bos": {
            "included": True,
            "description": "Protection & Balance of System",
            "quantity": 1.0,
            "unit_price": 0.0,
        },
        "civil": {
            "included": True,
            "description": "Civil works",
            "quantity": 1.0,
            "unit_price": 0.0,
        },
        "transportation": {
            "included": True,
            "description": "Transportation to site",
            "quantity": 1.0,
            "unit_price": 0.0,
        },
        "other": {
            "included": True,
            "description": "Other / Miscellaneous",
            "quantity": 1.0,
            "unit_price": 0.0,
        },
        "installation": {
            "mode": "Rate per kWp",
            "rate_per_kwp": 0.0,
            "manual_cost": 0.0,
        },
        "optional": {
            "metering": {
                "type": "Net Metering",
                "quantity": 1,
                "unit_price": 0.0,
                "include": False,
                "description": "Complete net metering / gross metering job including required documentation, application processing, coordination and related work as per applicable requirements.",
            },
            "earthing": {
                "type": "Complete Earthing",
                "quantity": 1,
                "unit_price": 0.0,
                "include": False,
                "description": "Complete earthing system for solar PV installation including required electrodes, conductors, connections and accessories.",
            },
            "lightning": {
                "type": "Conventional Lightning Arrestor",
                "quantity": 1,
                "unit_price": 0.0,
                "include": False,
                "description": "Lightning protection system including lightning arrestor, mounting accessories and required connections.",
            },
        },
        "discount_type": "Percentage",
        "discount_value": 0.0,
        "tax_rate": 0.0,
        "terms": DEFAULT_TERMS,
    }
