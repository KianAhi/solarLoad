from email.policy import default
from re import X
import sys

sys.path.append("./src")
sys.path.append("./data")
import PySimpleGUI as sg

from userInterfaces import startScreen, mainScreen, splashScreen
from pvgisApi import PVGIS

from house import House

def main():
    screenChoice = splashScreen()
    first = True
    while True:
        if screenChoice == "compare":
            if first:
                houses = [House()]
                first = False

            check = startScreen(houses)
            if type(check) == list:
                screenChoice = "mainScreen"
            elif check == "reset":
                first = True
        elif screenChoice == "gridScreen":
            break
        elif screenChoice == "mainScreen":
            break


if __name__ == "__main__":
    main()
    #h = [House(),House()]
    #startScreen(h)
