import PySimpleGUI as sg
import datetime
import calendar
import itertools

def popup_get_date(start_mon=None, start_day=None, start_year=None, end_month=None, end_day=None, end_year=None,  begin_at_sunday_plus=0, no_titlebar=True, title='Choose Date',  keep_on_top=True, location=(None, None), close_when_chosen=False, icon=None, locale=None, month_names=None, day_abbreviations=None):
    """
    Display a calendar window, get the user's choice, return as a tuple (mon, day, year)
    :param start_mon: The starting month
    :type start_mon: int
    :param start_day: The starting day - optional. Set to None or 0 if no date to be chosen at start
    :type start_day: int or None
    :param start_year: The starting year
    :type start_year: int
    :param begin_at_sunday_plus: Determines the left-most day in the display. 0=sunday, 1=monday, etc
    :type begin_at_sunday_plus: int
    :param icon: Same as Window icon parameter. Can be either a filename or Base64 value. For Windows if filename, it MUST be ICO format. For Linux, must NOT be ICO
    :type icon: str
    :param locale: locale used to get the day names
    :type locale: str
    :param month_names: optional list of month names to use (should be 12 items)
    :type month_names: List[str]
    :param day_abbreviations: optional list of abbreviations to display as the day of week
    :type day_abbreviations: List[str]
    :return: Tuple containing (month, day, year) of chosen date or None if was cancelled
    :rtype: None or (int, int, int)
    """

    if month_names is not None and len(month_names) != 12:
        sg.popup_error('Incorrect month names list specified. Must have 12 entries.', 'Your list:', month_names)

    if day_abbreviations is not None and len(day_abbreviations) != 7:
        sg.popup_error('Incorrect day abbreviation list. Must have 7 entries.', 'Your list:', day_abbreviations)

    day_font = 'TkFixedFont 9'
    mon_year_font = 'TkFixedFont 10'
    arrow_font = 'TkFixedFont 7'

    now = datetime.datetime.now()
    cur_month, cur_day, cur_year = now.month, now.day, now.year
    cur_month = start_mon or cur_month
    if start_mon is not None:
        cur_day = start_day
    else:
        cur_day = cur_day
    cur_year = start_year or cur_year


    def update_days(window, month, year, begin_at_sunday_plus, cal):
        [window[(cal, week, day)].update('') for cal in [cal] for day in range(7) for week in range(6)]
        weeks = calendar.monthcalendar(year, month)
        month_days = list(itertools.chain.from_iterable([[0 for _ in range(8 - begin_at_sunday_plus)]] + weeks))
        if month_days[6] == 0:
            month_days = month_days[7:]
            if month_days[6] == 0:
                month_days = month_days[7:]
        for i, day in enumerate(month_days):
            offset = i
            if offset >= 6 * 7:
                break
            window[(cal, offset // 7, offset % 7)].update(str(day) if day else '')

    def make_days_layout(cal):
        days_layout = []
        for week in range(6):
            row = []
            for day in range(7):
                row.append(sg.T('', size=(4, 1), justification='c', font=day_font, key=(cal, week, day), enable_events=True, pad=(0, 0)))
                #print((cal, week,day))
            days_layout.append(row)
        return days_layout


    # Create table of month names and week day abbreviations

    if day_abbreviations is None or len(day_abbreviations) != 7:
        fwday = calendar.SUNDAY
        try:
            if locale is not None:
                _cal = calendar.LocaleTextCalendar(fwday, locale)
            else:
                _cal = calendar.TextCalendar(fwday)
            day_names = _cal.formatweekheader(3).split()
        except Exception as e:
            print('Exception building day names from locale', locale,  e)
            day_names = ('Sun', 'Mon', 'Tue', 'Wed', 'Th', 'Fri', 'Sat')
    else:
        day_names = day_abbreviations

    mon_names = month_names if month_names is not None and len(month_names) == 12  else [calendar.month_name[i] for i in range(1,13)]
    #days_layout = make_days_layout()
    ############## CALENDAR 1 ###############
    calendarLayout_1 = [[sg.Text("Starting Date")]]
    calendarLayout_1 += [[
                sg.B('??????', font=arrow_font, border_width=0, key='-YEAR-DOWN-CAL1-', pad=((10,2),2)),
                sg.B('???', font=arrow_font, border_width=0, key='-MON-DOWN-CAL1-', pad=(0,2)),
                sg.Text('{} {}'.format(mon_names[cur_month - 1], cur_year), size=(16, 1), justification='c', font=mon_year_font, key='-MON-YEAR_CAL1-', pad=(0,2)),
                sg.B('???', font=arrow_font,border_width=0, key='-MON-UP-CAL1-', pad=(0,2)),
                sg.B('??????', font=arrow_font,border_width=0, key='-YEAR-UP-CAL1-', pad=(2,2))
    ]]

    calendarLayout_1 += [[sg.Col([[sg.T(day_names[i - (7 - begin_at_sunday_plus) % 7], size=(4,1), font=day_font, background_color=sg.theme_text_color(), text_color=sg.theme_background_color(), pad=(0,0)) for i in range(7)]], background_color=sg.theme_text_color(), pad=(0,0))]]
    calendarLayout_1 += make_days_layout(1)
    ############## CALENDAR 1 ###############

    # if not close_when_chosen:
    #     calendarLayout_1 += [[sg.Button('Ok', border_width=0,font='TkFixedFont 8'), sg.Button('Cancel',border_width=0, font='TkFixedFont 8')]]

    ############## CALENDAR 2 ###############
    calendarLayout_2 = [[sg.Text("Ending Date")]]
    calendarLayout_2 += [[sg.B('??????', font=arrow_font, border_width=0, key='-YEAR-DOWN-CAL2-', pad=((10,2),2)),
                sg.B('???', font=arrow_font, border_width=0, key='-MON-DOWN-CAL2-', pad=(0,2)),
                sg.Text('{} {}'.format(mon_names[end_month - 1], end_year), size=(16, 1), justification='c', font=mon_year_font, key='-MON-YEAR_CAL2-', pad=(0,2)),
                sg.B('???', font=arrow_font,border_width=0, key='-MON-UP-CAL2-', pad=(0,2)),
                sg.B('??????', font=arrow_font,border_width=0, key='-YEAR-UP-CAL2-', pad=(2,2))]
    ]

    calendarLayout_2 += [[sg.Col([[sg.T(day_names[i - (7 - begin_at_sunday_plus) % 7], size=(4,1), font=day_font, background_color=sg.theme_text_color(), text_color=sg.theme_background_color(), pad=(0,0)) for i in range(7)]], background_color=sg.theme_text_color(), pad=(0,0))]]
    calendarLayout_2 += make_days_layout(2)

    ############## CALENDAR 2 ###############
    

    # layout = [[ sg.Column([[sg.Text("Choose the starting Date")]] , calendarLayout_1),
    #             sg.Column([[sg.Text("Choose the ending Date")]],calendarLayout_2)
    # ]]
    layout = [[ calendarLayout_1 , calendarLayout_2, sg.Button('Ok', border_width=0,font='TkFixedFont 8'), sg.Button('Cancel',border_width=0, font='TkFixedFont 8')]]
    window = sg.Window(title, layout, no_titlebar=no_titlebar, grab_anywhere=True, keep_on_top=keep_on_top, font='TkFixedFont 12', use_default_focus=False, location=location, finalize=True, icon=icon)

    update_days(window, cur_month, cur_year, begin_at_sunday_plus,1)
    update_days(window, end_month, end_year, begin_at_sunday_plus,2)

    prev_choice = chosen_mon_day_year = None
    prev_choice_2 = chosen_mon_day_year_Ending =  None

    if cur_day:
        chosen_mon_day_year = cur_month, cur_day, cur_year
        for week in range(6):
            for day in range(7):
                if window[(1,week,day)].DisplayText == str(cur_day):
                    window[(1,week,day)].update(background_color=sg.theme_text_color(), text_color=sg.theme_background_color())
                    prev_choice = (1,week,day)
                    break

    if end_year is not None:
        chosen_mon_day_year_Ending = end_month, end_day, end_year
        for week in range(6):
            for day in range(7):
                if window[(2,week,day)].DisplayText == str(end_day):
                    window[(2,week,day)].update(background_color=sg.theme_text_color(), text_color=sg.theme_background_color())
                    prev_choice_2 = (2,week,day)
                    break
        
    
    while True:             # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            chosen_mon_day_year = None
            chosen_mon_day_year_Ending= None
            break
        if event == 'Ok':
            break
        if event in ('-MON-UP-CAL1-', '-MON-DOWN-CAL1-', '-YEAR-UP-CAL1-','-YEAR-DOWN-CAL1-'):
            cur_month += (event == '-MON-UP-CAL1-')
            cur_month -= (event == '-MON-DOWN-CAL1-')
            cur_year += (event == '-YEAR-UP-CAL1-')
            cur_year -= (event == '-YEAR-DOWN-CAL1-')
            if cur_month > 12:
                cur_month = 1
                cur_year += 1
            elif cur_month < 1:
                cur_month = 12
                cur_year -= 1
            window['-MON-YEAR_CAL1-'].update('{} {}'.format(mon_names[cur_month - 1], cur_year))
            update_days(window, cur_month, cur_year, begin_at_sunday_plus,1)
            if prev_choice:
                window[prev_choice].update(background_color=sg.theme_background_color(), text_color=sg.theme_text_color())

        elif event in ('-MON-UP-CAL2-', '-MON-DOWN-CAL2-', '-YEAR-UP-CAL2-','-YEAR-DOWN-CAL2-'):
            end_month += (event == '-MON-UP-CAL2-')
            end_month -= (event == '-MON-DOWN-CAL2-')
            end_year += (event == '-YEAR-UP-CAL2-')
            end_year -= (event == '-YEAR-DOWN-CAL2-')
            if end_month > 12:
                end_month = 1
                end_year += 1
            elif end_month < 1:
                end_month = 12
                end_year -= 1
            window['-MON-YEAR_CAL2-'].update('{} {}'.format(mon_names[end_month - 1], end_year))
            update_days(window, end_month, end_year, begin_at_sunday_plus,2)
            if prev_choice_2:
                window[prev_choice_2].update(background_color=sg.theme_background_color(), text_color=sg.theme_text_color())

        elif type(event) is tuple:
            if event[0] == 1:
                if window[event].DisplayText != "":
                    chosen_mon_day_year = cur_month, int(window[event].DisplayText), cur_year
                    if prev_choice:
                        window[prev_choice].update(background_color=sg.theme_background_color(), text_color=sg.theme_text_color())
                    window[event].update(background_color=sg.theme_text_color(), text_color=sg.theme_background_color())
                    prev_choice = event
                    if close_when_chosen:
                        break
            elif event[0] == 2:
                if window[event].DisplayText != "":
                    chosen_mon_day_year_Ending = end_month, int(window[event].DisplayText), end_year
                    if prev_choice_2:
                        window[prev_choice_2].update(background_color=sg.theme_background_color(), text_color=sg.theme_text_color())
                    window[event].update(background_color=sg.theme_text_color(), text_color=sg.theme_background_color())
                    prev_choice_2 = event
                    if close_when_chosen:
                        break
                
    window.close()
    return chosen_mon_day_year, chosen_mon_day_year_Ending



def initialGUI():
    layout = [[]]

if __name__ == "__main__":
    initialGUI()
    #print(popup_get_date(start_day=1,start_mon=1,start_year=2021,end_day=31,end_month=12,end_year=2021))