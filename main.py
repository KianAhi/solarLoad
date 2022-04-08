from email.policy import default
from re import X
import sys

sys.path.append("./src")
sys.path.append("./data")
import PySimpleGUI as sg

from userInterfaces import startScreen, mainScreen
from pvgisApi import PVGIS

from house import House

if __name__ == "__main__":
    h = House()
    startScreen([h])

    