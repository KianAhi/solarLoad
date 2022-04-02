import PySimpleGUI as sg
from radiationGUI import popup_get_date



if __name__ == "__main__":
    popup_get_date(start_day=1, start_mon=1, start_year=2021, end_day=31, end_month=12, end_year=2021)