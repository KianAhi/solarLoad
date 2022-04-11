from tracemalloc import start
import PySimpleGUI as sg
import sys
sys.path.append("../data")
from pvgisApi import PVGIS
from house import House


def splashScreen():
    """Creates a splash screen for the user to choose different from two differnt applications
    Returns:
        string: screen selction 
    """
    layout = [[sg.B("Compare House(s)",key="-COMP-"), sg.B("Evaluate Grid",key="-GRID-"), sg.B("Close",key="-CLOSE-")]]
    window = sg.Window("GUI chooser", layout, keep_on_top=True, grab_anywhere=True, finalize=True, no_titlebar=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "-CLOSE-"):
            exit()
        elif event == "-COMP-":
            window.close()
            screen = "compareScreen"
            break
        elif event == "-GRID-":
            window.close()
            screen = "gridScreen"
            break
    return screen

def mainScreen():
    pass


def fromGUItoClass(window, houses):
    """ Function to get all the Values untered in the GUI and update the corresponding class atributes
    Args: 
        window (PySimpleGUI window object): the current window object
        houses (list): list containing all instances of the House class
    Returns:
        list: houses
    """
    for i, house in enumerate(houses):
        for attr in dir(house):
            if callable(getattr(house, attr)) and attr.startswith("__"):
                continue

            if attr == "TECH":
                for tech in [(i, "crystSi"), (i, "CIS") , (i, "CdTe"), (i, "Unknown")]:
                    if window[tech].get() == True:
                        setattr(house, attr, tech[1])
                        continue

            for key in window.key_dict:
                if key == (i, f"-{str(attr)}-"):
                    setattr(house, attr, float(window[key].get()))
    return houses
    


def startScreen(houses, maxHouses = 5, pos = (None, None)):
    """Create the GUI for the User to input all the Values and start the API call
    Args:
        houses (list): list containing all instances of the House class
        maxHouses (int): Max number of houses that can be compared, default = 5
        pos (tuple): Position of the top left corner where the GUI should be placed
    Returns:
        list: list containing all instance of the House class
    """
    layout = [[]]
    counter = -1
    for house in houses:
        counter += 1
        generalOptions = [[sg.Text("Roofsize"),sg.Multiline(default_text=house.ROOFSIZE, key=(counter,"-ROOFSIZE-"),size = (10,1)), sg.Text("m^2")]
        ]
        pvgOptions = [[sg.Frame("Geographical Options",[[sg.Text("Latitude"), sg.Multiline(default_text=house.LAT, key=(counter,"-LAT-"), size = (10,1)), 
                    sg.Text("Longitude"), sg.Multiline(default_text = house.LON, key=(counter,"-LON-"), size = (10,1))],
                    [sg.Text("Slope"), sg.Multiline(default_text=house.SLOPE, key=(counter,"-SLOPE-"), size = (10,1)), 
                    sg.Text("Azimuth"), sg.Multiline(default_text = house.AZIMUTH, key=(counter,"-AZIMUTH-"), size = (10,1))]], border_width = 1)],
                    [sg.Frame("PV Technology",[[sg.Radio("crystSi",(counter,"technology"),key=(counter,'crystSi')),
                                                sg.Radio("CIS",(counter,"technology"),key=(counter,'CIS')),
                                                sg.Radio("CdTe",(counter,"technology"),key=(counter,'CdTe')),
                                                sg.Radio("Unknown",(counter,"technology"),key=(counter,'Unknown'))],
                                                [sg.Text("CO2 in production"), sg.Multiline(default_text=house.PAYBACK, key=(counter,"-PAYBACK-"), size = (10,1)), sg.Text("CO2/m^2") ]], border_width=1)],
                    [sg.Text("Watt Peak"), sg.Multiline(default_text=house.WATTPEAK, key=(counter,"-WATTPEAK-"), size = (10,1)),
                    sg.Text("Loss"), sg.Multiline(default_text=house.LOSS, key=(counter,"-LOSS-"),size=(10,1))  ],
        ]

        ecoOptions = [[sg.Frame("Returns",[
            [sg.Text("Energy selling price"), sg.Multiline(default_text=house.ENERGYPRICE, key=(counter,"-ENERGYPRICE-"),size = (10,1)),sg.Text("c/kWh")],
            [sg.Text("Share to the prop. owner"), sg.Multiline(default_text=house.SHARE, key=(counter,"-SHARE-"),size = (10,1)),sg.Text("%")],
            [sg.Text("Investment of the prop. owner"), sg.Multiline(default_text=house.INVESTMENTBYOWNER, key=(counter,"-INVESTMENTBYOWNER-"),size=(10,1)), sg.Text("€") ]], border_width=1)],
            [sg.Frame("Costs",[
                [sg.Text("PV-Costs"),sg.Multiline(default_text=house.PVCOSTS, key=(counter,"-PVCOSTS-"),size = (10,1)),sg.Text("€/m^2")],
                [sg.Text("Mounting-costs"),sg.Multiline(default_text=house.MOUNTINGCOSTS, key=(counter,"-MOUNTINGCOSTS-"),size = (10,1)),sg.Text("€/m^2")],
                [sg.Text("Connection costs"),sg.Multiline(default_text=house.CONNECTIONCOSTS, key=(counter,"-CONNECTIONCOSTS-"),size = (10,1)),sg.Text("€")],
                [sg.Text("Additional costs"),sg.Multiline(default_text=house.ADDITIONALCOSTS, key=(counter,"-ADDITIONALCOSTS-"),size = (10,1)),sg.Text("€")],
                ], border_width=1)],
        ]
        tempLayout = [[sg.Frame("General Options", layout = generalOptions)]]
        tempLayout += [[sg.Frame("PVG API Options", layout = pvgOptions)]]
        tempLayout += [[sg.Frame("Economical Params" ,layout = ecoOptions)]]
        layout[0].append(sg.Column([[sg.Frame(f"House {counter}", tempLayout)]]))

    layout += [[sg.Frame("",[[sg.Button("RUN",key="-START-" ), sg.Button("Exit",key="-EXIT-"),sg.Button("Reset",key="-RESET-"), sg.Button("Save as new Config",key="-SAVE-")]]),
    sg.Button("-",key="-SUB-",size=(2,1), ), sg.Button("+",key="-ADD-",size = (2,1))]]

    window = sg.Window("PVGIS solarLoad", layout, keep_on_top=False, grab_anywhere=True, resizable=True,location=pos, finalize=True)


    for i,house in enumerate(houses):
        window[(i, house.TECH)].update(True)

    while True:
        event, values = window.read()
        if event in  (sg.WIN_CLOSED,"-EXIT-"):
            exit()
        if event == "-RESET-":
            houses = [House()]
            window.close()
            startScreen(houses)
        if event == "-ADD-":
            if len(houses) < maxHouses:
                houses = fromGUItoClass(window, houses)
                houses.append(House())
                oldPos = window.current_location()
                window.close()
                startScreen(houses, pos = oldPos)
        if event == "-SUB-":
            if len(houses) != 1:
                houses.pop()
                houses = fromGUItoClass(window, houses)
                oldPos = window.current_location()
                window.close()
                startScreen(houses, pos = oldPos)
        if event == "-SAVE-":
            pass
        if event == "-START-":
            ret = fromGUItoClass(window,houses)
            window.close()
            return ret 
            # #popup_get_date(start_day=1, start_mon=1, start_year=2021, end_day=31, end_month=12, end_year=2021)
