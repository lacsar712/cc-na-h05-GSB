"""只读展示层：把巡检记录按数据库中各自的列原样取出并格式化。

measured_cd（实测光强，坎德拉）与 bearing_error_deg（方位偏差，度）
必须各自进入同名列、同名展示单元格，不得交叉读写。
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
