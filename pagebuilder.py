import datetime
import os
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from calendar import monthrange
from dateutil.relativedelta import relativedelta
import calendar
from datetime import date


# ---------------------------------------------------------------------------
# Constants — replacing long if/elif chains
# ---------------------------------------------------------------------------

MONTH_OFFSETS = {
    "JAN": 46.7645, "FEB": 46.154,  "MAR": 43.5305,
    "APR": 45.069,  "MAY": 44.464,  "JUN": 45.9905,
    "JUL": 48.875,  "AUG": 44.734,  "SEP": 45.1805,
    "OCT": 45.172,  "NOV": 44.5125, "DEC": 44.933,
}

MONTH_COLOURS = {
    1:  "#950000", 2:  "#009900", 3:  "#0048c6",
    4:  "#ffc409", 5:  "#964f79", 6:  "#0f8465",
    7:  "#F68716", 8:  "#0093ec", 9:  "#950000",
    10: "#009900", 11: "#0048c6", 12: "#0f8465",
}

# 28-day shift cycle starting 01/04/2022
SHIFT_CYCLE = [
    "CR1", "CR2", "CR3", "CR4", "CN1", "CN2", "CN3",
    "CR1", "CR2", "CR3", "CD1", "CD2",
    "CR1", "CR2", "CN1", "CN2", "CN3", "CN4",
    "CR1", "CR2", "CR3", "CD1", "CD2", "CD3",
    "CR1", "CR2", "CD1", "CD2",
]

# 12-day ExDays shift cycle starting 01/01/2022
SHIFT_EXDAYS_CYCLE = [
    "CL1", "CL2", "CL3", "CL4", "CR1", "CR2",
    "CE1", "CE2", "CE3", "CE4", "CR1", "CR2",
]


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def get_cdex_type():
    """Prompt the user for the Chronodex type."""
    return input("What type of Chronodex would you like to create? (Year, Month, Week): ")


def read_date(prompt):
    """Prompt for a date string in DD/MM/YYYY format, retrying on bad input."""
    while True:
        input_date = input(prompt)
        try:
            return datetime.datetime.strptime(input_date, "%d/%m/%Y")
        except ValueError:
            print("Unrecognised date format, please try again (DD/MM/YYYY)\n")


def init_date():
    """Return an error-checked start date from the user."""
    return read_date("Please enter start date for the Chronodex (DD/MM/YYYY)\n")


# ---------------------------------------------------------------------------
# Date utilities
# ---------------------------------------------------------------------------

def page_start_date(ps_date):
    """Rewind ps_date to the Monday of its week."""
    day_num = int(ps_date.strftime("%u"))  # 1=Mon … 7=Sun
    if day_num != 1:
        ps_date -= datetime.timedelta(days=day_num - 1)
    return ps_date


def get_start_date():
    """Get and normalise the user-supplied start date to the week's Monday."""
    return page_start_date(init_date())


def weeks_for_year(year):
    """Return the number of ISO weeks in the given year."""
    return date(year, 12, 28).isocalendar()[1]


def d_date(d_num, to_add):
    """
    Return the day number (d_num + to_add) as a zero-padded two-character string.
    d_num may be a string or int.
    """
    result = int(d_num) + to_add
    return f"{result:02d}"


def first_day_of_month(dt):
    """Return the weekday (0=Sun … 6=Sat) of the first day of dt's month."""
    first_day = datetime.datetime(dt.year, dt.month, 1)
    return first_day.strftime("%w")


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def mt_place(mt, side):
    """
    Return the X co-ordinate for centring the month abbreviation text.
    side is 'l' (left page) or 'r' (right page).
    """
    base = 0 if side == "l" else 417
    return base + MONTH_OFFSETS.get(mt, 0)


def select_colour(month):
    """Return the hex colour string for the given month number (1–12)."""
    return MONTH_COLOURS.get(month, "#000000")


# ---------------------------------------------------------------------------
# Shift pattern calculators
# ---------------------------------------------------------------------------

def calculate_shift(checkdate):
    """Return the shift code for checkdate based on the 28-day cycle."""
    shift_start = date(2022, 4, 1)
    checkdate = datetime.datetime.date(checkdate)
    delta = (checkdate - shift_start).days % 28
    return SHIFT_CYCLE[delta]


def calculate_shift_ex_days(checkdate):
    """Return the shift code for checkdate based on the 12-day ExDays cycle."""
    lates_start = date(2022, 1, 1)
    checkdate = datetime.datetime.date(checkdate)
    delta = (checkdate - lates_start).days % 12
    return SHIFT_EXDAYS_CYCLE[delta]


# ---------------------------------------------------------------------------
# Calendar display
# ---------------------------------------------------------------------------

def cal_display(dt, calendarbox, pageholder):
    """
    Fill calendar placeholder tokens in pageholder for either the current
    month (calendarbox=1) or next month (calendarbox=2).
    """
    pagestart_month = dt.month
    pagestart_year = dt.year
    next_month_obj = dt + relativedelta(months=1)

    pageholder = pageholder.replace("[CURRENTMONTH]", dt.strftime("%B"))
    pageholder = pageholder.replace("[NEXTMONTH]", next_month_obj.strftime("%B"))

    if calendarbox == 1:
        var_name = "CM"
        month_to_print = pagestart_month
        year_to_print = pagestart_year
    else:  # calendarbox == 2
        var_name = "NM"
        if pagestart_month == 12 and dt.day > 25:
            month_to_print = 1
            year_to_print = pagestart_year + 1
        else:
            month_to_print = pagestart_month + 1
            if month_to_print > 12:
                month_to_print = 1
            year_to_print = pagestart_year

    cal = calendar.Calendar()
    cal_box = 1
    for day in cal.itermonthdays(year_to_print, month_to_print):
        day_str = str(day) if day != 0 else ""
        pageholder = pageholder.replace(f"[{var_name}_D{cal_box}]", day_str)
        cal_box += 1

    # Clear any remaining placeholders if the month has fewer than 42 slots
    while cal_box < 43:
        pageholder = pageholder.replace(f"[{var_name}_D{cal_box}]", "")
        cal_box += 1

    return pageholder


# ---------------------------------------------------------------------------
# PDF output
# ---------------------------------------------------------------------------

def pdf_output(svg_file, filename):
    """Convert an SVG file to PDF, writing the PDF to the same path as svg_file."""
    pagebuild = svg2rlg(str(svg_file))
    renderPDF.drawToFile(pagebuild, str(filename) + ".pdf")


# ---------------------------------------------------------------------------
# Page creation
# ---------------------------------------------------------------------------

def pagecreate(pagedate, lr, output_dir):
    """
    Build one SVG page (left or right) for the week containing pagedate,
    write it to output_dir, and convert it to PDF.
    """
    day = pagedate.strftime("%d")
    month = pagedate.strftime("%b")
    month_upper = month.upper()
    year = pagedate.strftime("%Y")
    week = pagedate.strftime("%W")
    days_in_month = monthrange(pagedate.year, pagedate.month)[1]

    if lr == "l":
        # ------------------------------------------------------------------ #
        # Left-hand page
        # ------------------------------------------------------------------ #
        with open("Chronodex_pl.svg") as f:
            pageholder = f.read()

        pageholder = pageholder.replace("[DATE1]", day)

        next_day = int(d_date(day, 1))
        if next_day < days_in_month:
            pageholder = pageholder.replace("[DATE2]", d_date(day, 1))
            pageholder = pageholder.replace("[DATE3]", d_date(day, 2))
        elif next_day > days_in_month:
            pageholder = pageholder.replace("[DATE2]", "01")
            pageholder = pageholder.replace("[DATE3]", "02")
        else:  # next_day == days_in_month
            pageholder = pageholder.replace("[DATE2]", d_date(day, 1))
            pageholder = pageholder.replace("[DATE3]", "01")

        month_colour = select_colour(pagedate.month)
        month_position = mt_place(month_upper, "l")

        pageholder = pageholder.replace("[MONTHCOLOUR]", month_colour)
        pageholder = pageholder.replace("[MONTHPOSITION]", str(month_position))
        pageholder = pageholder.replace("[MONTH]", month_upper)
        pageholder = pageholder.replace("[YEAR]", year)
        pageholder = pageholder.replace("[WEEKNUMBER]", week)

        # Shift pattern placeholders cleared (feature not currently required)
        pageholder = pageholder.replace("[CHR1]", "")
        pageholder = pageholder.replace("[CHR2]", "")
        pageholder = pageholder.replace("[CHR3]", "")

        svg_name = output_dir / f"{year}_p{week}{lr}.svg"
        with open(svg_name, "w") as wf:
            wf.write(pageholder)

    elif lr == "r":
        # ------------------------------------------------------------------ #
        # Right-hand page
        # ------------------------------------------------------------------ #
        with open("Chronodex_pr.svg") as f:
            pageholder = f.read()

        month_colour = select_colour(pagedate.month)
        pagemonth = month_upper

        day3 = int(d_date(day, 3))

        if day3 == days_in_month:
            pageholder = pageholder.replace("[DATER1]", d_date(day, 3))
            pageholder = pageholder.replace("[DATER2]", "01")
            pageholder = pageholder.replace("[DATER3]", "02")
            pageholder = pageholder.replace("[DATER4]", "03")
            next_month_obj = pagedate + relativedelta(months=1)
            month_colour = select_colour(next_month_obj.month)
            pagemonth = next_month_obj.strftime("%b").upper()

        elif day3 > days_in_month:
            days_over = day3 - days_in_month
            pageholder = pageholder.replace("[DATER1]", f"{days_over:02d}")
            pageholder = pageholder.replace("[DATER2]", f"{days_over + 1:02d}")
            pageholder = pageholder.replace("[DATER3]", f"{days_over + 2:02d}")
            pageholder = pageholder.replace("[DATER4]", f"{days_over + 3:02d}")
            next_month_obj = pagedate + relativedelta(months=1)
            month_colour = select_colour(next_month_obj.month)
            pagemonth = next_month_obj.strftime("%b").upper()

        else:  # day3 < days_in_month
            pageholder = pageholder.replace("[DATER1]", d_date(day, 3))
            pageholder = pageholder.replace("[DATER2]", d_date(day, 4))

            day5 = int(d_date(day, 5))
            day6 = int(d_date(day, 6))

            if day5 <= days_in_month:
                pageholder = pageholder.replace("[DATER3]", d_date(day, 5))
            else:
                days_over = day5 - days_in_month
                pageholder = pageholder.replace("[DATER3]", f"{days_over:02d}")

            if day6 <= days_in_month:
                pageholder = pageholder.replace("[DATER4]", d_date(day, 6))
            else:
                days_over = day6 - days_in_month
                pageholder = pageholder.replace("[DATER4]", f"{days_over:02d}")

        month_position = mt_place(month_upper, "r")
        pageholder = pageholder.replace("[MONTHCOLOUR]", month_colour)
        pageholder = pageholder.replace("[MONTHPOSITION]", str(month_position))
        pageholder = pageholder.replace("[MONTH]", pagemonth)
        pageholder = pageholder.replace("[YEAR]", year)
        pageholder = pageholder.replace("[WEEKNUMBER]", week)

        pageholder = cal_display(pagedate, 1, pageholder)
        pageholder = cal_display(pagedate, 2, pageholder)

        # Shift pattern placeholders cleared (feature not currently required)
        pageholder = pageholder.replace("[CHRR1]", "")
        pageholder = pageholder.replace("[CHRR2]", "")
        pageholder = pageholder.replace("[CHRR3]", "")
        pageholder = pageholder.replace("[CHRR4]", "")

        svg_name = output_dir / f"{year}_p{week}{lr}.svg"
        with open(svg_name, "w") as wf:
            wf.write(pageholder)

    pdf_output(svg_name, output_dir / f"{year}_p{week}{lr}")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def create_chronodex(ctype, start_date):
    """Generate Chronodex pages for a week, month, or full year."""
    ctype = ctype.strip().lower()
    pagedate = start_date

    # Create ~/chronodex_DDMMYYYY output folder based on start_date
    folder_name = "chronodex_" + start_date.strftime("%d-%m-%Y")
    output_dir = Path.home() / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output folder: {output_dir}")

    if ctype == "month":
        print("Start Date:", start_date)
        num_weeks = len(calendar.monthcalendar(pagedate.year, pagedate.month))
        for _ in range(num_weeks):
            print("Page Date:", pagedate)
            pagecreate(pagedate, "l", output_dir)
            pagecreate(pagedate, "r", output_dir)
            pagedate += relativedelta(weeks=1)

    elif ctype == "year":
        print("Start Date:", start_date)
        for _ in range(1, 13):
            num_weeks = len(calendar.monthcalendar(pagedate.year, pagedate.month))
            for _ in range(num_weeks):
                print("Page Date:", pagedate)
                pagecreate(pagedate, "l", output_dir)
                pagecreate(pagedate, "r", output_dir)
                pagedate += relativedelta(weeks=1)

    else:
        # Default: single week
        pagecreate(start_date, "l", output_dir)
        pagecreate(start_date, "r", output_dir)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cdex_type = get_cdex_type()
    start_date = get_start_date()
    create_chronodex(cdex_type, start_date)
