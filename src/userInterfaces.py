import PySimpleGUI as sg
import sys
sys.path.append("../data")
from house import House
import yaml
import os

def saveConfigQuestionnaire(amountHouses, oldNames):
    layout = [[sg.Text("Select the Home you want to save as new config and give it a name")],
    [sg.Text("Specify a Name for the new config") ,sg.Multiline(default_text="", key="-CONFIG-", expand_x=True, enter_submits=True)]]
    layout += [[sg.Radio(f"House {houseSelection+1}", group_id="house", key=houseSelection) for houseSelection in range(0,amountHouses)]]
    layout += [[sg.B("OK", s=10, key="-OK-"), sg.B("Cancel", s=10, key="-EXIT_POPUP-")]]

    window = sg.Window('Config Saver', layout, finalize=True)
    window[0].update(True)

    while True:
        event, value = window.read()
        if event == "-OK-" or event == "-CONFIG-":
            if len(window['-CONFIG-'].get()) > 0:
                if window['-CONFIG-'].get() in oldNames:
                    sg.popup_ok("Config Name already exists. Please chooose another name")
                    continue
                for c in range(0,amountHouses):
                    if window[c].get() == True:
                        returnValue = window['-CONFIG-'].get().strip()
                        window.close()
                        return (c, returnValue)
            else:
                sg.popup_ok("Config name can't be empty",title="ERROR")
        elif event == "-EXIT_POPUP-":
            return (None, None)

def saveNewConfig(window, houses, yaml_path = None , houseSelection = 0):
    maxConfigs = 10
    if yaml_path == None:
        yaml_path = os.path.join(os.path.dirname(__file__), "../data/defaultValues.yaml")

    with open(yaml_path, 'r') as stream:
        index = "default"
        try:
            load = yaml.safe_load(stream)
            keyList = [key for key in load[index]]
        except yaml.YAMLError as exc:
            print(exc)

    presentConfigs = [key for key in load]
    strippedConfigs = presentConfigs.copy()
    strippedConfigs.remove("default")
    houseSelection, configName = saveConfigQuestionnaire(len(houses), presentConfigs)


    if houseSelection == None:
        return

    configName = configName.replace(" ","_")

    if len(load) == maxConfigs:
        layout = [[sg.Text(f"There are more than {maxConfigs} present, already. \n Please choose one to be deleted")],
        [sg.Combo(strippedConfigs, default_value = strippedConfigs[0], expand_x = True, key="DDLIST")],
        [sg.Button("OK",key="-OK-"), sg.Button("Cancel")]
        ]
        popup_window = sg.Window("Choose configs",layout,finalize=True)
        while True:
            events, _ = popup_window.read()
            if events == "-OK-":
                load.pop(popup_window["DDLIST"].get())
                popup_window.close()
                break
            else:
                return
    
    load[configName] = {}
    for variable in keyList:
        if variable == "TECH":
            for tech in [(houseSelection, "crystSi"), (houseSelection, "CIS") , (houseSelection, "CdTe"), (houseSelection, "Unknown")]:
                if window[tech].get() == True:
                    load[configName]["TECH"] = str(tech[1])
        for key in window.key_dict:
            if key == (houseSelection, f"-{str(variable)}-"):
                load[configName][variable] = float(window[(houseSelection, f"-{str(variable)}-")].get())
    with open(yaml_path, 'w') as file:
        yaml.dump(load, file, sort_keys=False)
    sg.popup_ok("New configuration saved succesfully!")

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
    for houseSelection, house in enumerate(houses):
        for variable in dir(house):
            if callable(getattr(house, variable)) and variable.startswith("__"):
                continue

            if variable == "TECH":
                for tech in [(houseSelection, "crystSi"), (houseSelection, "CIS") , (houseSelection, "CdTe"), (houseSelection, "Unknown")]:
                    if window[tech].get() == True:
                        setattr(house, variable, tech[1])
                        continue

            for key in window.key_dict:
                if key == (houseSelection, f"-{str(variable)}-"):
                    setattr(house, variable, float(window[key].get()))
    return houses
    


def startScreen(houses, maxHouses = 5, pos = (None, None), configList = None, yaml_path = None, valueTemplate = "default"):
    """Create the GUI for the User to input all the Values and start the API call
    Args:
        houses (list): list containing all instances of the House class
        maxHouses (int): Max number of houses that can be compared, default = 5
        pos (tuple): Position of the top left corner where the GUI should be placed
    Returns:
        list: list containing all instance of the House class
    """
    if configList == None:
        if yaml_path == None:
            yaml_path = os.path.join(os.path.dirname(__file__), "../data/defaultValues.yaml")
        with open(yaml_path, 'r') as stream:
            try:
                load = yaml.safe_load(stream)
                keyList = [key for key in load]
            except yaml.YAMLError as exc:
                print(exc)


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
            [sg.Text("Energy selling price"), sg.Multiline(default_text=house.ENERGYPRICE, key=(counter,"-ENERGYPRICE-"),size = (10,1)),sg.Text("ct/kWh")],
            [sg.Text("Share to the prop. owner"), sg.Multiline(default_text=house.SHARE, key=(counter,"-SHARE-"),size = (10,1)),sg.Text("%")],
            [sg.Text("Investment of the prop. owner"), sg.Multiline(default_text=house.INVESTMENTBYOWNER, key=(counter,"-INVESTMENTBYOWNER-"),size=(10,1)), sg.Text("€") ]], border_width=1)],
            [sg.Frame("Costs",[
                [sg.Text("PV-Costs"),sg.Multiline(default_text=house.PVCOSTS, key=(counter,"-PVCOSTS-"),size = (10,1)),sg.Text("€/m^2")],
                [sg.Text("Mounting-costs"),sg.Multiline(default_text=house.MOUNTINGCOSTS, key=(counter,"-MOUNTINGCOSTS-"),size = (10,1)),sg.Text("€/m^2")],
                [sg.Text("Connection costs"),sg.Multiline(default_text=house.CONNECTIONCOSTS, key=(counter,"-CONNECTIONCOSTS-"),size = (10,1)),sg.Text("€")],
                [sg.Text("Hardware costs"),sg.Multiline(default_text=house.HARDWARECOSTS, key=(counter,"-HARDWARECOSTS-"),size = (10,1)),sg.Text("€")],
                [sg.Text("Insurance costs"),sg.Multiline(default_text=house.INSURANCECOSTS, key=(counter,"-INSURANCECOSTS-"),size = (10,1)),sg.Text("€/year")],
                [sg.Text("Storage"),sg.Multiline(default_text=house.STORAGECOSTS, key=(counter,"-STORAGECOSTS-"),size = (10,1)),sg.Text("€/kWh")],
                [sg.Text("Additional costs"),sg.Multiline(default_text=house.ADDITIONALCOSTS, key=(counter,"-ADDITIONALCOSTS-"),size = (10,1)),sg.Text("€")],
                ], border_width=1)],
        ]
        tempLayout = [[sg.Frame("General Options", layout = generalOptions)]]
        tempLayout += [[sg.Frame("PVG API Options", layout = pvgOptions)]]
        tempLayout += [[sg.Frame("Economical Params" ,layout = ecoOptions)]]
        tempLayout += [[sg.Combo(keyList, default_value = house.yamlIndex, key=(counter,"-CONFIGURATION-"), enable_events=True)]]
        layout[0].append(sg.Column([[sg.Frame(f"House {counter}", tempLayout)]]))

    layout += [[sg.Frame("",[[sg.Button("RUN",key="-START-" ), sg.Button("Exit",key="-EXIT-"),sg.Button("Reset",key="-RESET-"), sg.Button("Save as new Config",key="-SAVE-")]]),
    sg.Button("-",key="-SUB-",size=(2,1), ), sg.Button("+",key="-ADD-",size = (2,1))]]

    # if valueTemplate != "default"
    #     if counter == 1:
    #         layout.insert(0, [sg.Combo(keyList, default_value = valueTemplate  ,key="-CONFIGUTATION-", enable_events=True)])
    #     else:    
    #         layout[len(layout)-1] +=  [sg.Combo(keyList, default_value = valueTemplate  ,key="-CONFIGUTATION-", enable_events=True)]

    window = sg.Window("PVGIS solarLoad", layout, keep_on_top=False, grab_anywhere=True, resizable=True,location=pos, finalize=True)

    configurationKeys = []
    for houseSelection,house in enumerate(houses):
        window[(houseSelection, house.TECH)].update(True)
        configurationKeys.append((houseSelection,"-CONFIGURATION-")) 

    while True:
        event, values = window.read()
        if event in  (sg.WIN_CLOSED, "-EXIT-"):
            exit()
        if event == "-RESET-":
            houses = [House()]
            oldPos = window.current_location()
            window.close()
            startScreen(houses, oldPos)
        if event in configurationKeys:
            houses = fromGUItoClass(window, houses)
            oldPos = window.current_location()
            print(window[event].get()+ "_________")
            houses[event[0]] = House(index = window[event].get() )
            window.close()
            return startScreen(houses, pos = oldPos)
        if event == "-ADD-":
            if len(houses) < maxHouses:
                houses = fromGUItoClass(window, houses)
                houses.append(House())
                oldPos = window.current_location()
                window.close()
                return startScreen(houses, pos = oldPos)
        if event == "-SUB-":
            if len(houses) != 1:
                houses.pop()
                houses = fromGUItoClass(window, houses)
                oldPos = window.current_location()
                window.close()
                return startScreen(houses, pos = oldPos)
        if event == "-SAVE-":
            saveNewConfig(window,houses)
            pass
        if event == "-START-":
            ret = fromGUItoClass(window,houses)
            window.close()
            return ret 
            # #popup_get_date(start_day=1, start_mon=1, start_year=2021, end_day=31, end_month=12, end_year=2021)
