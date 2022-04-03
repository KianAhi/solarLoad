import sys
sys.path.append("./src")
import PySimpleGUI as sg
from radiationGUI import popup_get_date
import pvgisApi 


if __name__ == "__main__":
    layout = [ 
            [sg.Multiline(default_text = "Please Insert Latitude",key="-LAT-" )],
            [sg.Multiline(default_text = "Please Insert Longitude",key="-LON-" )],
            [sg.Multiline(default_text = "Please Insert Peak Power",key="-PP-" )],
            [sg.Multiline(default_text = "Please Insert Energy Cost in cent",key="-ECOST-" )],
            [sg.Multiline(default_text = "Please Insert Setup Cost",key="-SCOST-" )],
            [sg.Multiline(default_text = "crystSI",key="-pvTechChoice-" )],
            [sg.Multiline(default_text = "Please Insert Loss",key="-LOSS-" )],
            [sg.Multiline(default_text = "Please Insert Latitude",key="-LAT-" )],
            [sg.B("Start",key="-START-")]
    ]
    window = sg.Window("Test",layout,finalize=True)

    while True:
        event, values = window.read()
        if event == "Close":
            break
        if event == "-START-":
            # test = pvgisApi.PVGIS()
            # test.set_value("lat", float(window['-LAT-'].get()))
            # test.set_value("lon", float(window['-LON-'].get()))
            # test.set_value("peakpower",  float(window['-PP-'].get()))
            # test.set_value("optimalinclination", 1)
            # test.set_value("optimalangles", 1)
            # test.send_api_request()
            # data = test.get_data(print_output=True)
            popup_get_date(start_day=1, start_mon=1, start_year=2021, end_day=31, end_month=12, end_year=2021)