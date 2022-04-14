import sys

sys.path.append("./src")
sys.path.append("./data")
import PySimpleGUI as sg

from userInterfaces import startScreen, mainScreen, splashScreen
from pvgisApi import PVGIS

from house import House

def main():
    screenChoice = splashScreen()
    compareScreen()

def compareScreen(houses = None):
    if houses == None:
        houses = startScreen([House()])
    else:
        houses = startScreen(houses)

    for i, house in enumerate(houses):
        house.calculate_peak_power()
        house.create_pv()
        errorCheck = house.simulate_pv()
        if errorCheck != 0:
            choice, _ = sg.Window('Continue?', [[sg.T(f"{errorCheck} in house {i+1}")], [sg.B("Try again", s=10, key="-AGAIN-"), sg.B("New start", s=10, key="-NEW-"), sg.B("Exit", s=10, key="-EXIT_POPUP-")]], disable_close=True).read(close=True)
            if choice == "-AGAIN-":
                compareScreen(houses)
            elif choice == "-NEW-":
                main()
            elif choice == "-EXIT_POPUP-":
                exit()
        house.calculate_investment_costs()
        house.calculate_running_costs()
        house.calculate_revenue()
        house.calculate_profit()
        house.plotGraph()
    mainScreen(houses)

if __name__ == "__main__":
    main()
    #h = [House(),House()]
    #startScreen(h)
