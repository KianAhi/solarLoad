from calendar import monthrange
from itsdangerous import json
from pandas import date_range
from datetime import date, timedelta

startDate = date(2020, 1, 1)
endDate = date(2021, 12, 31)

years = [2020,2021]

def getCalendarEntries(startDate, endDate):
    my_dict = {}
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    hours = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    years = []
    for i in range(startDate.year - endDate.year + 1):
        years.append(startDate.year + i)

    for year in years:
        my_dict[year] = {}
        for month in months:
            my_dict[year][month] = {}
            _, days = monthrange(year, months.index(month)+1)
            for day in range(1,days+1):
                my_dict[year][month][day] = {}
                for hour in hours:
                    my_dict[year][month][day][hour] = "NettoValue"
