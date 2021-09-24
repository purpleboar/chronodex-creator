import datetime
import svglib
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM


def read_date(prompt, def_date=None):
    #Error checked data capture called by init_date
    success = True
    while success == 1:
        input_date = input(prompt) #or def_date
        try:
            input_date = datetime.datetime.strptime(input_date,'%d/%m/%Y')
            success = False
        except ValueError:
            print('Unrecognized date format, please try again\n')
    return input_date

def init_date():
    #used to call error checked date and return result.
    return read_date("Please enter start date for the Chronodex (DD/MM/YYYY)\n")

def get_start_date():
    s_date = init_date()
    #week_num = s_date.strftime("%W")
    day_num = int(s_date.strftime("%u"))
    if day_num != 1:
        #-1 from day_num and then subtract that number of days from start_date to make the date the start of the week.
        past_start = datetime.timedelta(days=day_num-1)
        s_date = s_date - past_start
    return s_date

def d_date (d_num, to_add):
    d_num = str(int(d_num)+to_add)
    if len(d_num) == 1: d_num = "0" + d_num
    return d_num

def mt_place (mt):
    #Month Text Placement
    if mt == "JAN": startpt = 46.7645
    elif mt == "FEB": startpt = 46.154
    elif mt == "MAR": startpt = 43.5305
    elif mt == "APR": startpt = 45.069
    elif mt == "MAY": startpt = 44.464
    elif mt == "JUN": startpt = 45.9905
    elif mt == "JUL": startpt = 48.875
    elif mt == "AUG": startpt = 44.734
    elif mt == "SEP": startpt = 45.1805
    elif mt == "OCT": startpt = 45.172
    elif mt == "NOV": startpt = 44.5125
    elif mt == "DEC": startpt = 44.933


    return startpt

def pdfoutput(svgfile,filename):
    #Open the svg file and process as a pdf
    pagebuild = svg2rlg(svgfile)
    renderPDF.drawToFile(pagebuild, filename + ".pdf")



def pagecreate(pagedate, lr):
    #if pagedate.strftime("%u") > "1": pagedate = pagedate 
    day = pagedate.strftime("%d") 
    month = pagedate.strftime("%b")
    year = pagedate.strftime("%Y")
    week = pagedate.strftime("%W")

    #Variables set up in Chronodex_pl.svg and Chronodex_pr.svg
    #[FILENAME] = final svg file name
    #[MONTHCOLOUR] = colour code #000000
    #[MONTHPOSITION] = X Co-ordinates to centre month text
    #[MONTH] = 3 character month
    #[YEAR] = 4 digit week number
    #[WEEKNUMBER] = 2 digit week number
    #[DATE1] = 2 digit date first day
    #[DATE2] = 2 digit date second day
    #[DATE3] = 2 digit date third day
    #[DATER1] = 2 digit date first day - right page
    #[DATER2] = 2 digit date second day - right page
    #[DATER3] = 2 digit date third day - right page
    #[DATER4] = 2 digit date fourth day - right page
    #[CHR1] = CHR rota day 1 in left page
    #[CHR2] = CHR rota day 2 in left page
    #[CHR3] = CHR rota day 3 in left page
    #[CHRR1] = CHR rota day 1 in right page
    #[CHRR2] = CHR rota day 2 in right page
    #[CHRR3] = CHR rota day 3 in right page
    #[CHRR4] = CHR rota day 4 in right page
    #[CURRENTMONTH] = Current month for calendar on right page
    #[CM_D#] = Current month day#
    #[NEXTMONTH] = Next month for calendar on right page
    #[NM_D#] = Next month day#
    

    if lr == "l":
        file = open('Chronodex_pl.svg')
        pageholder = file.read()
        file.close
        pageholder = pageholder.replace("[MONTHCOLOUR]", "#009900")
        pageholder = pageholder.replace("[MONTHPOSITION]", str(mt_place(month.upper())))
        pageholder = pageholder.replace("[MONTH]", month.upper())
        pageholder = pageholder.replace("[YEAR]", year)
        pageholder = pageholder.replace("[WEEKNUMBER]", week)
        pageholder = pageholder.replace("[DATE1]", day)
        pageholder = pageholder.replace("[DATE2]", d_date(day,1)) 
        pageholder = pageholder.replace("[DATE3]", d_date(day,2))
        pageholder = pageholder.replace("[CHR1]", "CR")
        pageholder = pageholder.replace("[CHR2]", "CE")
        pageholder = pageholder.replace("[CHR3]", "CL")
        wfile = open(year + "_p" + week + lr + ".svg","w")
        wfile.write(pageholder)
        wfile.close
    elif lr == "r":
        file = open('Chronodex_pr.svg')
        pageholder = file.read()
        file.close
        pageholder = pageholder.replace("[MONTHCOLOUR]", "#009900")
        pageholder = pageholder.replace("[MONTH]", month.upper())
        pageholder = pageholder.replace("[YEAR]", year)
        pageholder = pageholder.replace("[WEEKNUMBER]", week)
        pageholder = pageholder.replace("[DATER1]", d_date(day,3))
        pageholder = pageholder.replace("[DATER2]", d_date(day,4))
        pageholder = pageholder.replace("[DATER3]", d_date(day,5))
        pageholder = pageholder.replace("[DATER4]", d_date(day,6))
        pageholder = pageholder.replace("[CHRR1]", "CR")
        pageholder = pageholder.replace("[CHRR2]", "CE")
        pageholder = pageholder.replace("[CHRR3]", "CL")
        pageholder = pageholder.replace("[CHRR4]", "CL")
        wfile = open(year + "_p" + week + lr + ".svg","w")
        wfile.write(pageholder)
        wfile.close

    pdfoutput(year +"_p" + week + lr + ".svg", year +"_p" + week + lr)
"""
date_entry = input('Enter a date in YYYY-MM-DD format: ')
y, m, d = map(int, date_entry.split('-'))
user_date = datetime.date(y, m, d)
pagecreate (user_date,"l")
"""

start_date = get_start_date()

pagecreate (start_date,"l")
pagecreate (start_date,"r")