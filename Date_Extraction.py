import re
import string

numbs = "(^a(?=\s)|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)"
day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
week_day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
exp1 = "(before|after|earlier|later|ago)"
exp2 = "(this|next|last)"
month = "(january|february|march|april|may|june|july|august|september|october|november|december)"
date_month_year = "(year|day|week|month)"
rel_day = "(today|yesterday|tomorrow|tonight|tonite)"
iso = "\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+"
year = "((?<=\s)\d{4}|^\d{4})"
regexxp1 = "((\d+|(" + numbs + "[-\s]?)+) " + date_month_year + "s? " + exp1 + ")"
regexxp2 = "(" + exp2 + " (" + date_month_year + "|" + week_day + "|" + month + "))"

date = "([012]?[0-9]|3[01])"
regexxp3 = "(" + date + " " + month + " " + year + ")"
regexxp4 = "(" + month + " " + date + "[th|st|rd]?[,]? " + year + ")"

regex1 = re.compile(regexxp1, re.IGNORECASE)
regex2 = re.compile(regexxp2, re.IGNORECASE)
regex3 = re.compile(rel_day, re.IGNORECASE)
regex4 = re.compile(iso)
regex5 = re.compile(year)
regex6 = re.compile(regexxp3, re.IGNORECASE)
regex7 = re.compile(regexxp4, re.IGNORECASE)

def extractDate(text):

    # Initialization
    timex_found = []

    # re.findall() finds all the substring matches, keep only the full
    # matching string. Captures expressions such as 'number of days' ago, etc.
    my_find = regex1.findall(text)
    my_find = [a[0] for a in my_find if len(a) > 1]
    for timex in my_find:
        timex_found.append(timex)

    # Variations of this thursday, next year, etc
    my_find = regex2.findall(text)
    my_find = [a[0] for a in my_find if len(a) > 1]
    for timex in my_find:
        timex_found.append(timex)

    # today, tomorrow, etc
    my_find = regex3.findall(text)
    for timex in my_find:
        timex_found.append(timex)

    # ISO
    my_find = regex4.findall(text)
    for timex in my_find:
        timex_found.append(timex)

    # Dates
    my_find = regex6.findall(text)
    my_find = [a[0] for a in my_find if len(a) > 1]
    for timex in my_find:
        timex_found.append(timex)

    my_find = regex7.findall(text)
    my_find = [a[0] for a in my_find if len(a) > 1]
    for timex in my_find:
        timex_found.append(timex)

    # Year
    my_find = regex5.findall(text)
    for timex in my_find:
        timex_found.append(timex)
   

    return timex_found