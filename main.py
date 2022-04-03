import sys
sys.path.append("./src")
sys.path.append("./data")
import PySimpleGUI as sg

import json
from defaultValues import * 
from userInterfaces import startScreen
from pvgisApi import PVGIS

if __name__ == "__main__":
    startScreen()

    