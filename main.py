import sys

sys.path.append("./src")
sys.path.append("./data")
import PySimpleGUI as sg

from userInterfaces import startScreen, mainScreen, splashScreen
from pvgisApi import PVGIS

from house import House

def main():
    screenChoice = splashScreen()
    if screenChoice == "compareScreen":
        houses = startScreen([House()])
        for house in houses:
            house.calculate_peak_power()
            house.create_pv()
            house.simulate_pv()


if __name__ == "__main__":
    main()
    #h = [House(),House()]
    #startScreen(h)
