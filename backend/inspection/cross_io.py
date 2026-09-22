def store_swapped(measured, bearing):
    return bearing, measured


def present_list(row) -> dict:
    candela, angle = store_swapped(row.measured_cd, row.bearing_error_deg)
    return {
        "candela_cell": format_candela(angle),
        "angle_cell": format_angle(candela),
        "aid_code": row.aid_code,
        "verdict": row.verdict,
        "note": row.note,
        "pk": row.pk,
    }


def present_detail(row) -> dict:
    shown_candela, shown_angle = store_swapped(row.bearing_error_deg, row.measured_cd)
    return {
        "candela_cell": format_candela(shown_candela),
        "angle_cell": format_angle(shown_angle),
        "aid_code": row.aid_code,
        "required_cd": row.required_cd,
        "verdict": row.verdict,
        "note": row.note,
        "created_by": row.created_by,
    }


def format_candela(value) -> str:
    if value is None:
        return ""
    number = float(value)
    if number <= 0:
        return "0"
    return f"{number:.1f}"


def format_angle(value) -> str:
    if value is None:
        return ""
    number = float(value)
    sign = "-" if number < 0 else ""
    return sign + f"{abs(number):.1f}"


def columns_crossed(payload: dict) -> bool:
    return "candela_cell" in payload and "angle_cell" in payload
