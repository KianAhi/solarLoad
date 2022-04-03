import PySimpleGUI as sg
from matplotlib.font_manager import json_load
from radiationGUI import popup_get_date
import sys
import json
sys.path.append("./src")

from pvgisApi import PVGIS

def readDefaultValues():
    with open("./data/defaultValues",'r') as f:
        vars = json.load(f)

    for var in vars['variables'][0]:
        globals()[var] = vars['variables'][0][var]

if __name__ == "__main__":
    #solarEval = PVGIS()
    readDefaultValues()
    
    pvgOptions = [[sg.Text("Latitude"), sg.Multiline(default_text=defaultLat, key="-LAT-", size = (10,1)), 
                sg.Text("Longitude"), sg.Multiline(default_text = defaultLon, key="-LON-", size = (10,1))],
                [sg.Frame("PV Technology",[[sg.Radio("crystSi","technology",key='crystSi'),
                                            sg.Radio("CIS","technology",key='CIS'),
                                            sg.Radio("CdTe","technology",key='CdTe'),
                                            sg.Radio("Unknown","technology",key='Unknown')]], border_width=1)],
                [sg.Text("Peak Power"), sg.Multiline(default_text=defaultPp, key="-PP-", size = (10,1)),
                sg.Text("Loss"), sg.Multiline(default_text=defaultLoss, key="-LOSS-" ,size=(10,1))  ],
    ]

    ecoOptions = [[sg.Text("cent/kWh"),sg.Multiline(default_text=defaultEnergyPrice, key="-ENERGY_PRICE-")]


    ]
    layout = [[sg.Frame("PVG API Options", layout = pvgOptions)]]
    layout+= [[sg.Frame("Economical Params" ,layout = ecoOptions)]]
    window = sg.Window("Test", layout, keep_on_top=True, grab_anywhere=True, finalize=True)

    #Update to default Values
    window[defaultTech].update(True)

    while True:
        event, values = window.read()
        if event == "Close" or event == "-EXIT-":
            break
        if event == "-START-":
            pass
            # test = pvgisApi.PVGIS()
            # test.set_value("lat", float(window['-LAT-'].get()))
            # test.set_value("lon", float(window['-LON-'].get()))
            # test.set_value("peakpower",  float(window['-PP-'].get()))
            # test.set_value("optimalinclination", 1)
            # test.set_value("optimalangles", 1)
            # test.send_api_request()
            # data = test.get_data(print_output=True)
            #popup_get_date(start_day=1, start_mon=1, start_year=2021, end_day=31, end_month=12, end_year=2021)