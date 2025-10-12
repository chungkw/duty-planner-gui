import calendar
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

from utils import add_leading_zero

CALENDAR_MONTHS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

DAYS_OF_WEEK = {
    0: "MON",
    1: "TUE",
    2: "WED",
    3: "THU",
    4: "FRI",
    5: "SAT",
    6: "SUN",
}


class WriterConfig:
    def __init__(self, output_path: str, output_file_name: str, duty_year: int, duty_month: int,
                 public_holidays: list[int],
                 show_individual_blocked_pct: bool):
        self.output_path = output_path
        self.output_file_name = output_file_name
        self.duty_year = duty_year
        self.duty_month = duty_month
        self.last_duty_month = 12 if duty_month == 1 else duty_month - 1
        self.public_holidays = public_holidays
        self.show_individual_blocked_pct = show_individual_blocked_pct


def writer(duty_clerks: list, writer_config: WriterConfig):
    # HOW TO COUNT WITH OFFSET
    # nth cells after offset
    # S/N, rank, name, branch, blocked?
    offset_col_srnbb = 4 if writer_config.show_individual_blocked_pct else 3
    offset_headers = 2

    clerk_count = len(duty_clerks)

    # What is the first weekday of the month and number of days in month
    first_weekday, no_of_days = calendar.monthrange(writer_config.duty_year, writer_config.duty_month)

    sheet_name = f"{CALENDAR_MONTHS[writer_config.duty_month]} {writer_config.duty_year}"

    workbook = xlsxwriter.Workbook(f"{writer_config.output_path}/{writer_config.output_file_name}")
    worksheet = workbook.add_worksheet(name=sheet_name)

    # Styling for different cells
    default_style = workbook.add_format()
    default_style.set_border()

    # Default for text cells
    centre_style = workbook.add_format()
    centre_style.set_align("center")
    centre_style.set_border()

    # Bold font for title
    title_style = workbook.add_format()
    title_style.set_align("center")
    title_style.set_border()
    title_style.set_bold()

    # Background colour for block-out dates
    blocked_style = workbook.add_format()
    blocked_style.set_align("center")
    blocked_style.set_border()
    blocked_style.set_bg_color("#92D050")

    # Highlight duty
    highlight_style = workbook.add_format()
    highlight_style.set_align("center")
    highlight_style.set_border()
    highlight_style.set_bg_color("#EA9999")
    highlight_style.set_bold()

    # Highlight reserve
    info_style = workbook.add_format()
    info_style.set_align("center")
    info_style.set_border()
    info_style.set_bg_color("#D8D8D8")
    info_style.set_bold()

    # Background colour for weekends
    weekend_style = workbook.add_format()
    weekend_style.set_align("center")
    weekend_style.set_border()
    weekend_style.set_bg_color("#B8CCE4")

    # Background colour for PH
    ph_style = workbook.add_format()
    ph_style.set_align("center")
    ph_style.set_border()
    ph_style.set_bg_color("#FFD966")

    # Warn if there are no duty/reserve personnel on a day
    warning_style = workbook.add_format()
    warning_style.set_align("center")
    warning_style.set_border()
    warning_style.set_bg_color("#FF0000")

    # HEADERS

    # Header rows
    worksheet.merge_range(
        0,
        offset_col_srnbb + 1,
        0,
        offset_col_srnbb + no_of_days,
        sheet_name,
        title_style,
    )

    worksheet.merge_range(0, 0, 2, 0, "S/N", centre_style)
    worksheet.merge_range(0, 1, 2, 1, "Rank", centre_style)
    worksheet.merge_range(0, 2, 2, 2, "Name", centre_style)
    worksheet.merge_range(0, 3, 2, 3, "Branch", centre_style)
    if writer_config.show_individual_blocked_pct:
        worksheet.merge_range(0, 4, 2, 4, "PCs", centre_style)

    worksheet.merge_range(
        0,
        offset_col_srnbb + no_of_days + 1,
        1,
        offset_col_srnbb + no_of_days + 3,
        "Points",
        centre_style,
    )

    for i, x in enumerate(
            [
                "Duties",
                "Reserves",
                "Remarks",
            ]
    ):
        cur_col = offset_col_srnbb + no_of_days + 3 + i + 1
        worksheet.merge_range(0, cur_col, 2, cur_col, x, centre_style)

    for i, x in enumerate(
            [
                CALENDAR_MONTHS[writer_config.last_duty_month],
                CALENDAR_MONTHS[writer_config.duty_month],
                "Total",
            ]
    ):
        cur_col = offset_col_srnbb + no_of_days + 1 + i
        worksheet.write_string(2, cur_col, x, centre_style)

    calendar_dates = [x for x in range(1, no_of_days + 1)]

    weekend_dates = [
        x
        for i, x in enumerate(calendar_dates)
        if DAYS_OF_WEEK[(first_weekday + i) % 7] == "SAT"
           or DAYS_OF_WEEK[(first_weekday + i) % 7] == "SUN"
    ]

    calendar_weekdays = [
        DAYS_OF_WEEK[x % 7] for x in range(first_weekday, first_weekday + no_of_days)
    ]

    for i, x in enumerate(calendar_dates):
        cur_col = offset_col_srnbb + 1 + i

        style = centre_style if x not in weekend_dates else weekend_style
        style = style if x not in writer_config.public_holidays else ph_style

        worksheet.write_string(1, cur_col, str(x), style)

    for i, x in enumerate(calendar_weekdays):
        cur_col = offset_col_srnbb + 1 + i
        cur_date = i + 1

        style = centre_style if cur_date not in weekend_dates else weekend_style
        style = style if cur_date not in writer_config.public_holidays else ph_style

        worksheet.write_string(2, cur_col, x, style)

    for i, x in enumerate(["Duties", "Reserves"]):
        cur_row = offset_headers + clerk_count + 1 + i
        worksheet.merge_range(cur_row, 0, cur_row, offset_col_srnbb, x, centre_style)

    # WRITE CALENDAR

    total_days = clerk_count * no_of_days
    total_blocked_days = 0

    total_weekend_days = clerk_count * len(weekend_dates)
    total_blocked_weekend_days = 0

    # Write calendar for every day per clerk
    for i, person in enumerate(duty_clerks):
        cur_row = offset_headers + 1 + i

        # Count only PC
        clerk_blocked_days = 0

        # Write and format every cell on clerk row for every day of month
        for date in calendar_dates:
            cur_col = offset_col_srnbb + date

            if date in person["requests"]:
                cell_style = centre_style

                # Blend into background colour
                if date in weekend_dates:
                    cell_style = weekend_style
                elif date in writer_config.public_holidays:
                    cell_style = ph_style

                worksheet.write_string(cur_row, cur_col, "·", cell_style)

            elif date in person["leaves"]:
                worksheet.write_string(cur_row, cur_col, "LVE", blocked_style)
                total_blocked_days += 1
                if date in weekend_dates:
                    total_blocked_weekend_days += 1
                # clerk_blocked_days += 1

            elif date in person["offs"]:
                worksheet.write_string(cur_row, cur_col, "OFF", blocked_style)
                total_blocked_days += 1
                if date in weekend_dates:
                    total_blocked_weekend_days += 1
                # clerk_blocked_days += 1

            elif date in person["ar"]:
                worksheet.write_string(cur_row, cur_col, "AR", blocked_style)
                total_blocked_days += 1
                if date in weekend_dates:
                    total_blocked_weekend_days += 1
                # clerk_blocked_days += 1

            elif date in person["ma"]:
                worksheet.write_string(cur_row, cur_col, "MA", blocked_style)
                total_blocked_days += 1
                if date in weekend_dates:
                    total_blocked_weekend_days += 1
                # clerk_blocked_days += 1

            elif date in person["pc"]:
                worksheet.write_string(cur_row, cur_col, "PC", blocked_style)
                total_blocked_days += 1
                if date in weekend_dates:
                    total_blocked_weekend_days += 1
                clerk_blocked_days += 1

            # Blank cells are here
            else:
                cell_style = centre_style

                if date in weekend_dates:
                    cell_style = weekend_style

                if date in writer_config.public_holidays:
                    cell_style = ph_style

                worksheet.write_string(cur_row, cur_col, "", cell_style)

        clerk_blocked_pct = int((clerk_blocked_days / no_of_days) * 100)

        # S/N, rank, name, branch, blocked pct
        # Placeholder values for rank and branch
        person_info = [
            (add_leading_zero(i + 1), centre_style),
            ("", default_style),
            (person["name"], default_style),
            ("", default_style),
        ]

        if writer_config.show_individual_blocked_pct:
            person_info.append(
                (
                    str(clerk_blocked_pct) + "%",
                    centre_style if clerk_blocked_pct < 50 else highlight_style,
                )
            )

        for j, (x, s) in enumerate(person_info):
            worksheet.write_string(cur_row, j, x, s)

    # Apply style on empty cells on duty points and remarks columns
    for i in range(clerk_count):
        cur_row = offset_headers + 1 + i
        cur_col = offset_col_srnbb + no_of_days + 1

        # Last month
        worksheet.write_string(cur_row, cur_col, "", centre_style)
        # This month
        worksheet.write_string(cur_row, cur_col + 1, "", centre_style)
        # Remarks
        worksheet.write_string(cur_row, cur_col + 5, "", centre_style)

    # Narrow width for S/N and date columns
    worksheet.set_column(0, 0, 4)
    worksheet.set_column(offset_col_srnbb + 1, offset_col_srnbb + no_of_days, 4)

    # COUNTING DUTIES PER DAY AND PER CLERK

    # Count duties and reserves per day
    for i in range(1, no_of_days + 1):
        cur_row = offset_headers + clerk_count
        cur_col = offset_col_srnbb + i

        formula_range = (
            xl_rowcol_to_cell(offset_headers + 1, cur_col),
            xl_rowcol_to_cell(offset_headers + clerk_count, cur_col),
        )

        formula_x = f'=COUNTIF({formula_range[0]}:{formula_range[1]},"X")'
        formula_r = f'=COUNTIF({formula_range[0]}:{formula_range[1]},"R")'

        worksheet.write_formula(cur_row + 1, cur_col, formula_x, centre_style)
        worksheet.write_formula(cur_row + 2, cur_col, formula_r, centre_style)

    # Sum of duty points and count duties and reserves per clerk
    for i in range(clerk_count):
        cur_row = offset_headers + 1 + i
        cur_col = offset_col_srnbb + no_of_days

        formula_range_s = (
            xl_rowcol_to_cell(cur_row, cur_col + 1),
            xl_rowcol_to_cell(cur_row, cur_col + 2),
        )

        formula_range_xr = (
            xl_rowcol_to_cell(cur_row, offset_col_srnbb + 1),
            xl_rowcol_to_cell(cur_row, offset_col_srnbb + no_of_days),
        )

        formula_s = f"=SUM({formula_range_s[0]}:{formula_range_s[1]})"
        formula_x = f'=COUNTIF({formula_range_xr[0]}:{formula_range_xr[1]},"X")'
        formula_r = f'=COUNTIF({formula_range_xr[0]}:{formula_range_xr[1]},"R")'

        worksheet.write_formula(cur_row, cur_col + 3, formula_s, centre_style)
        worksheet.write_formula(cur_row, cur_col + 4, formula_x, centre_style)
        worksheet.write_formula(cur_row, cur_col + 5, formula_r, centre_style)

    # CONDITIONAL FORMATTING

    # Highlight duty
    duty_highlight_cf_options = {
        "type": "cell",
        "criteria": "==",
        "value": '"X"',
        "format": highlight_style,
    }

    duty_highlight_cf_range = (
        xl_rowcol_to_cell(offset_headers + 1, offset_col_srnbb + 1),
        xl_rowcol_to_cell(offset_headers + clerk_count, offset_col_srnbb + no_of_days),
    )

    worksheet.conditional_format(
        f"{duty_highlight_cf_range[0]}:{duty_highlight_cf_range[1]}",
        duty_highlight_cf_options,
    )

    # Highlight reserve
    reserve_highlight_cf_options = {
        "type": "cell",
        "criteria": "==",
        "value": '"R"',
        "format": info_style,
    }

    worksheet.conditional_format(
        f"{duty_highlight_cf_range[0]}:{duty_highlight_cf_range[1]}",
        reserve_highlight_cf_options,
    )

    # Highlight days with no duty or reserve
    day_xr_nil_cf_options = {
        "type": "cell",
        "criteria": "!=",
        "value": 1,
        "format": warning_style,
    }

    day_xr_nil_cf_range = (
        xl_rowcol_to_cell(offset_headers + clerk_count + 1, offset_col_srnbb + 1),
        xl_rowcol_to_cell(
            offset_headers + clerk_count + 2, offset_col_srnbb + no_of_days
        ),
    )

    worksheet.conditional_format(
        f"{day_xr_nil_cf_range[0]}:{day_xr_nil_cf_range[1]}",
        day_xr_nil_cf_options,
    )

    # Highlight clerks with no duty or reserve
    clerk_xr_nil_cf_options = {
        "type": "cell",
        "criteria": "<",
        "value": 1,
        "format": warning_style,
    }

    clerk_xr_nil_cf_range = (
        xl_rowcol_to_cell(offset_headers + 1, offset_col_srnbb + no_of_days + 4),
        xl_rowcol_to_cell(
            offset_headers + clerk_count, offset_col_srnbb + no_of_days + 5
        ),
    )

    worksheet.conditional_format(
        f"{clerk_xr_nil_cf_range[0]}:{clerk_xr_nil_cf_range[1]}",
        clerk_xr_nil_cf_options,
    )

    # META INFO

    total_blocked_pct = int((total_blocked_days / total_days) * 100)
    total_blocked_weekend_pct = int(
        (total_blocked_weekend_days / total_weekend_days) * 100
    )

    for i, (k, v, vs) in enumerate(
            [
                (
                        "Clerks",
                        str(clerk_count),
                        centre_style if clerk_count > 15 else highlight_style,
                ),
                (
                        "Blocked",
                        str(total_blocked_pct) + "%",
                        centre_style if total_blocked_pct < 50 else highlight_style,
                ),
                (
                        "Weekends",
                        str(total_blocked_weekend_pct) + "%",
                        centre_style
                ),
            ]
    ):
        cur_row = offset_headers + clerk_count + 4 + i
        cur_col = 1

        worksheet.write_string(cur_row, cur_col, k, default_style)
        worksheet.write_string(cur_row, cur_col + 1, v, vs)

    worksheet.freeze_panes("A4")

    workbook.close()
