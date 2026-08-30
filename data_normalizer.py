from datetime import datetime


def clean_text(value):
    """Clean text fields and handle missing values."""

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_date(value):
    """Convert dates into YYYY-MM-DD format."""

    if not value:
        return None

    value = str(value).strip()

    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            date = datetime.strptime(value, fmt)
            return date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def clean_number(value):
    """Convert numeric values safely."""

    if value is None or value == "":
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def normalize_deal(item):
    """Convert a raw Monday Deal into a clean dictionary."""

    columns = {
        column["id"]: column["text"]
        for column in item["column_values"]
    }

    return {
        "deal_name": clean_text(item["name"]),

        "owner_code": clean_text(
            columns.get("color_mm6qhx5b")
        ),

        "client_code": clean_text(
            columns.get("dropdown_mm6qzh5")
        ),

        "deal_status": clean_text(
            columns.get("color_mm6qntm5")
        ),

        "actual_close_date": clean_date(
            columns.get("date_mm6qhzbm")
        ),

        "closure_probability": clean_text(
            columns.get("color_mm6q1q81")
        ),

        "deal_value": clean_number(
            columns.get("numeric_mm6qha0")
        ),

        "tentative_close_date": clean_date(
            columns.get("date_mm6qyn7s")
        ),

        "deal_stage": clean_text(
            columns.get("color_mm6q1dx3")
        ),

        "product_deal": clean_text(
            columns.get("color_mm6q6xk4")
        ),

        "sector": clean_text(
            columns.get("color_mm6qc7cq")
        ),

        "created_date": clean_date(
            columns.get("date_mm6qztxn")
        ),
    }


def normalize_work_order(item):
    """Convert a raw Monday Work Order into a clean dictionary."""

    columns = {
        column["id"]: column["text"]
        for column in item["column_values"]
    }

    return {
        "work_order_name": clean_text(item["name"]),

        "deal_name": clean_text(
            columns.get("dropdown_mm6q6m31")
        ),

        "customer_code": clean_text(
            columns.get("dropdown_mm6qbr99")
        ),

        "nature_of_work": clean_text(
            columns.get("color_mm6qjq2d")
        ),

        "execution_status": clean_text(
            columns.get("color_mm6qhcj0")
        ),

        "data_delivery_date": clean_date(
            columns.get("date_mm6qvdfb")
        ),

        "po_loi_date": clean_date(
            columns.get("date_mm6qykzk")
        ),

        "document_type": clean_text(
            columns.get("color_mm6qa0g9")
        ),

        "probable_start_date": clean_date(
            columns.get("date_mm6q26c3")
        ),

        "probable_end_date": clean_date(
            columns.get("date_mm6qng9f")
        ),

        "owner_code": clean_text(
            columns.get("color_mm6q44v9")
        ),

        "sector": clean_text(
            columns.get("color_mm6q5vv8")
        ),

        "type_of_work": clean_text(
            columns.get("color_mm6q2ns")
        ),

        "software_platform": clean_text(
            columns.get("color_mm6q8t1s")
        ),

        "last_invoice_date": clean_date(
            columns.get("date_mm6qdx78")
        ),

        "latest_invoice_no": clean_text(
            columns.get("dropdown_mm6q97bk")
        ),

        "amount_excl_gst": clean_number(
            columns.get("numeric_mm6q6wj6")
        ),

        "amount_incl_gst": clean_number(
            columns.get("numeric_mm6qcmts")
        ),

        "billed_value_excl_gst": clean_number(
            columns.get("numeric_mm6qrvf0")
        ),

        "billed_value_incl_gst": clean_number(
            columns.get("numeric_mm6q1y23")
        ),

        "collected_amount": clean_number(
            columns.get("numeric_mm6qftqt")
        ),

        "amount_to_be_billed_excl_gst": clean_number(
            columns.get("numeric_mm6qwxmj")
        ),

        "amount_to_be_billed_incl_gst": clean_number(
            columns.get("numeric_mm6qrxyq")
        ),

        "amount_receivable": clean_number(
            columns.get("numeric_mm6qvemw")
        ),

        "ar_priority": clean_text(
            columns.get("color_mm6qf444")
        ),

        "quantity_by_ops": clean_number(
            columns.get("numeric_mm6q81wt")
        ),

        "quantity_as_per_po": clean_number(
            columns.get("dropdown_mm6qfvam")
        ),

        "quantity_billed": clean_number(
            columns.get("numeric_mm6qhyry")
        ),

        "balance_quantity": clean_number(
            columns.get("numeric_mm6qf32")
        ),

        "invoice_status": clean_text(
            columns.get("color_mm6qjgv3")
        ),

        "actual_billing_month": clean_text(
            columns.get("color_mm6q9f0r")
        ),

        "wo_status_billed": clean_text(
            columns.get("color_mm6qshvm")
        ),

        "billing_status": clean_text(
            columns.get("color_mm6qyp8y")
        ),
    }