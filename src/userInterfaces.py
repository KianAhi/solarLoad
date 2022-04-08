import PySimpleGUI as sg
import sys
sys.path.append("../data")
from pvgisApi import PVGIS
import os


def mainScreen():
    pass

def startScreen(houses):
    for house in houses:
        counter = 0
        generalOptions = [[sg.Text("Roofsize"),sg.Multiline(default_text=house.ROOFSIZE, key="-ROOF-SIZE-",size = (10,1)), sg.Text("m^2")]
        ]
        pvgOptions = [[sg.Frame("Geographical Options",[[sg.Text("Latitude"), sg.Multiline(default_text=house.LAT, key="-LAT-", size = (10,1)), 
                    sg.Text("Longitude"), sg.Multiline(default_text = house.LON, key="-LON-", size = (10,1))],
                    [sg.Text("Slope"), sg.Multiline(default_text=house.SLOPE, key="-SLOPE-", size = (10,1)), 
                    sg.Text("Azimuth"), sg.Multiline(default_text = house.AZIMUTH, key="-AZIMUTH-", size = (10,1))]], border_width = 1)],
                    [sg.Frame("PV Technology",[[sg.Radio("crystSi","technology",key='crystSi'),
                                                sg.Radio("CIS","technology",key='CIS'),
                                                sg.Radio("CdTe","technology",key='CdTe'),
                                                sg.Radio("Unknown","technology",key='Unknown')],
                                                [sg.Text("CO2 in production"), sg.Multiline(default_text=house.PAYBACK, key="-PACKBACK-", size = (10,1)), sg.Text("CO2/m^2") ]], border_width=1)],
                    [sg.Text("Watt Peak"), sg.Multiline(default_text=house.WATTPEAK, key="-WP-", size = (10,1)),
                    sg.Text("Loss"), sg.Multiline(default_text=house.LOSS, key="-LOSS-" ,size=(10,1))  ],
        ]

        ecoOptions = [[sg.Frame("Returns",[
            [sg.Text("Energy selling price"), sg.Multiline(default_text=house.ENERGYPRICE, key="-ENERGY_PRICE-",size = (10,1)),sg.Text("c/kWh")],
            [sg.Text("Share to the prop. owner"), sg.Multiline(default_text=house.SHARE, key="-SHARE_TO_OWNER-",size = (10,1)),sg.Text("%")],
            [sg.Text("Investment of the prop. owner"), sg.Multiline(default_text=house.INVESTMENTBYOWNER, key="-INV_BY_OWNER-",size=(10,1)), sg.Text("€") ]], border_width=1)],
            [sg.Frame("Costs",[
                [sg.Text("PV-Costs"),sg.Multiline(default_text=house.PVCOSTS, key="-PV_COSTS-",size = (10,1)),sg.Text("€/m^2")],
                [sg.Text("Mounting-costs"),sg.Multiline(default_text=house.MOUNTINGCOSTS, key="-MOUNT_COSTS-",size = (10,1)),sg.Text("€/m^2")],
                [sg.Text("Connection costs"),sg.Multiline(default_text=house.CONNECTIONCOSTS, key="-CON_COSTS-",size = (10,1)),sg.Text("€")],
                [sg.Text("Additional costs"),sg.Multiline(default_text=house.ADDITIONALCOSTS, key="-ADD_COSTS-",size = (10,1)),sg.Text("€")],
                ], border_width=1)],
        ]
        layout = [[sg.Frame("General Options", layout = generalOptions)]]
        layout += [[sg.Frame("PVG API Options", layout = pvgOptions)]]
        layout += [[sg.Frame("Economical Params" ,layout = ecoOptions)]]
        layout += [[sg.Frame("",[[sg.Button("RUN",key="-START-" ), sg.Button("Exit",key="-EXIT-"),sg.Button("Reset",key="-RESET-"), sg.Button("Save as new Config",key="-SAVE-")]]),
        sg.Button("-",key="-SUB-",size=(2,1)), sg.Button("+",key="-ADD-",size = (2,1))]]

    window = sg.Window("Test", layout, keep_on_top=True, grab_anywhere=True, finalize=True)

    #Update to default Values
    #window[house.TECH].update(True)

    while True:
        event, values = window.read()
        if event in  (sg.WIN_CLOSED,"-EXIT-"):
            break
        if event == "-RESET-":
            return 2
        if event == "-START-":
#            pass
            test = pvgisApi.PVGIS()
            test.set_value("lat", float(window['-LAT-'].get()))
            test.set_value("lon", float(window['-LON-'].get()))
            test.set_value("peakpower",  float(window['-PP-'].get()))
            test.set_value("optimalinclination", 1)
            test.set_value("optimalangles", 1)
            test.send_api_request()
            data = test.get_data(print_output=True)
            #popup_get_date(start_day=1, start_mon=1, start_year=2021, end_day=31, end_month=12, end_year=2021)

if __name__ == "__main__":
    mainScreen()