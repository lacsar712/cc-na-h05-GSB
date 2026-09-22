"""巡检记录的列展示映射。

实测光强（坎德拉）只进 measured_cd / candela_cell，
方位偏差（度）只进 bearing_error_deg / angle_cell，
任何展示路径都不得对调这两列。
"""


def present_list(row) -> dict:
    return {
        "candela_cell": format_candela(row.measured_cd),
        "angle_cell": format_angle(row.bearing_error_deg),
        "aid_code": row.aid_code,
        "verdict": row.verdict,
        "note": row.note,
        "pk": row.pk,
    }


def present_detail(row) -> dict:
    return {
        "candela_cell": format_candela(row.measured_cd),
        "angle_cell": format_angle(row.bearing_error_deg),
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
