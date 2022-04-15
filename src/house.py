from importlib.metadata import metadata
import os
from setuptools_scm import meta
import yaml
import pvgisApi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import numpy as np
from PIL import Image, ExifTags
import io
import base64
import pickle
import json

import piexif
import piexif.helper


class House:

    def __init__(self, yaml_path=None, index="default" ):
        """load object variables from a .yaml file
        if a path to a .yaml file is passed use it, otherwise load the defaultValues.yaml
        """
        if yaml_path == None:
            yaml_path = os.path.join(os.path.dirname(__file__), "../data/defaultValues.yaml")
        try:
            with open(yaml_path, 'r') as stream:
                try:
                    load = yaml.safe_load(stream)
                    for key in load[index]:
                        setattr(self, key, load[index][key])
                except yaml.YAMLError as exc:
                    print(exc)
        except FileNotFoundError as Err:
            print("There is no .yaml file at %s" % yaml_path)
            raise
        self.yamlIndex = index
        self.houseName = None

    def plotGraph(self, size = (500,500)):
        """plotting the data from the PVGIS API
        """
        years = np.linspace(0,20,21)
        costs = self.investment_costs + self.running_costs * years
        
        rev_list = []
        for i,time in enumerate(years):
            rev_list.append(self.revenue * i+1)
        
        profit_list = []
        for i,time in enumerate(years):
            profit_list.append(self.profit * i+1)
        
        plt.figure()
        plt.plot(years,costs,label = "Costs")
        plt.plot(years,rev_list,label = "Revenue")
        plt.plot(years,profit_list,label = "Profit")
        plt.legend()
        fig = plt.gcf()
        image = self.figure_to_image(fig)
        return self.convert_to_bytes(image, size)

    def calculate_peak_power(self):
        """calculate the peak power from the roof area and the watt peak per m^2 of
        the solar cell technology. (wattpeak can be used to test different technologies)

        Returns:
            float: PeakPower in kWp
        """
        return self.ROOFSIZE * self.WATTPEAK/1000
    
    def create_pv(self):
        """creating a pvgis object to get the data from the PVGIS API

        Returns:
            PVGIS: pvgisAPI object
        """
        pvgis_api_obj = pvgisApi.PVGIS()
        pvgis_api_obj.set_value('lat', self.LAT)
        pvgis_api_obj.set_value('lon', self.LAT)
        pvgis_api_obj.set_value('pvtechchoice', self.TECH)
        pvgis_api_obj.set_value('loss', self.LOSS)
        pvgis_api_obj.set_value('angle', self.SLOPE)
        pvgis_api_obj.set_value('aspect', self.AZIMUTH)
        pvgis_api_obj.set_value('peakpower', self.calculate_peak_power())
        
        return pvgis_api_obj
    
    def simulate_pv(self):
        """creates a virtual pv system from the object variables, sends the API request and saves the returned data
        in an object variable self.pv_data"""

        pv_system = self.create_pv()
        returnCheck = pv_system.send_api_request()
        if returnCheck == 0:
            self.pv_data = pv_system.get_data()
            return 0
        else:
            return returnCheck
        
    def check_for_data(self):
        """checking if the PV system has already been simulated. If not returns false and generates a print.

        Returns:
            bool: if data exists -> True
        """
        if hasattr(self, 'pv_data'):
            return True
        else:
            print("PV-Data has not yet been generated!")
            return False
    
    def get_data_for_house(self, case):
        """simple helper function to query data from the self.pv_data dict

        Args:
            case (str): key name of datapoint in the self.pv_data dict
        """
        if self.check_for_data():
            try:
                return self.pv_data[case][0]
            except KeyError as KeyExc:
                print(KeyExc)
    
    def calculate_investment_costs(self):
        """calculates the investment costs

        Returns:
            float: one-time investment costs 
        """
        inv_cost = self.PVCOSTS * self.ROOFSIZE
        inv_cost += self.MOUNTINGCOSTS 
        inv_cost += self.CONNECTIONCOSTS
        inv_cost += self.ADDITIONALCOSTS
        inv_cost += self.STORAGECOSTS
        inv_cost += self.HARDWARECOSTS
        inv_cost += self.ADDITIONALCOSTS
        inv_cost -= self.INVESTMENTBYOWNER
        #inv_cost += self.INSURANCECOSTS
        setattr(self, "investment_costs", inv_cost)
        return inv_cost
    
    def calculate_running_costs(self):
        """calculates the running costs

        Returns:
            float: running costs per year
        """
        run_cost = (self.get_data_for_house('E_y') * self.ENERGYPRICE) * (self.SHARE/100)
        run_cost += self.INSURANCECOSTS
        setattr(self, 'running_costs', run_cost)
        return run_cost
    
    def calculate_revenue(self):
        """calculate the revenue from selling power to the grid

        Returns:
            float: revenue
        """
        revenue = (self.get_data_for_house('E_y') * self.ENERGYPRICE)
        setattr(self, 'revenue', revenue)
        return revenue

    def calculate_profit(self):
        """calculate the profit which is the sales from selling power to the grid minus the "Pachtgebuehren"

        Returns:
            float: profit
        """
        profit = self.revenue - self.running_costs
        setattr(self, 'profit', profit)
        return profit

    def figure_to_image(self,figure):
        """
        Draws the previously created "figure" in the supplied Image Element
        :param element: an Image Element
        :param figure: a Matplotlib figure
        :return: The figure canvas
        """

        plt.close('all')        # erases previously drawn plots
        canv = FigureCanvasAgg(figure)
        buf = io.BytesIO()
        canv.print_figure(buf, format='png')
        if buf is None:
            return None
        buf.seek(0)
        return buf.read()

    def convert_to_bytes(self, file_or_bytes, resize=None):
        '''
        Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
        Turns into  PNG format in the process so that can be displayed by tkinter
        :param file_or_bytes: either a string filename or a bytes base64 image object
        :type file_or_bytes:  (Union[str, bytes])
        :param resize:  optional new size
        :type resize: (Tuple[int, int] or None)
        :return: (bytes) a byte-string object
        :rtype: (bytes)
        '''
        if isinstance(file_or_bytes, str):
            img = Image.open(file_or_bytes)
        else:
            try:
                img = Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
            except Exception as e:
                dataBytesIO = io.BytesIO(file_or_bytes)
                img = Image.open(dataBytesIO)

        cur_width, cur_height = img.size
        if resize:
            new_width, new_height = resize
            scale = min(new_height/cur_height, new_width/cur_width)
            img = img.resize((int(cur_width*scale), int(cur_height*scale)), Image.ANTIALIAS)
        with io.BytesIO() as bio:
            img.save(bio, format="PNG")
            del img
            return bio.getvalue()

    def metaDataToExif(self, images, filepath = "./"):
        """Writing the class instance's variables as metadata to an image file
        Read the Data:

        """
        metaData = {}
        for variable in dir(self):
            if callable(getattr(self, variable)) or variable.startswith("__"):
                continue
            metaData[str(variable)] = getattr(a, variable)
        exif_dict = {"0th": {}, "Exif": {}, "1st": {},
            "thumbnail": None, "GPS": {}}
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
            pickle.dumps(metaData),
            encoding="unicode")

        data = piexif.insert(
            piexif.dump(exif_dict),
        )
        images.save(filepath, exif=data)
if __name__ == "__main__":
    a = House()
    a.metaDataToExif(Image.new(500,500))
