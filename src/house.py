import os
import yaml
import pvgisApi

class House:

    def __init__(self, yaml_path=None):
        """load object variables from a .yaml file
        if a path to a .yaml file is passed use it, otherwise load the defaultValues.yaml
        """
        if yaml_path == None:
            yaml_path = os.path.join(os.path.dirname(__file__), "../data/defaultValues.yaml")
        try:
            with open(yaml_path, 'r') as stream:
                index = "config"
                try:
                    load = yaml.safe_load(stream)
                    for key in load[index]:
                        setattr(self, key, load[index][key])
                except yaml.YAMLError as exc:
                    print(exc)
        except FileNotFoundError as Err:
            print("There is no .yaml file at %s" % yaml_path)
            raise
    
    def calculate_peak_power(self):
        """calculate the peak power from the roof area and the watt peak per m^2 of
        the solar cell technology. (wattpeak can be used to test different technologies)

        Returns:
            float: PeakPower in kWp
        """
        return self.ROOFSIZE * self.WATTPEAK
    
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
        pv_system.send_api_request()
        self.pv_data = pv_system.get_data()
    
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
                self.pv_data[case][0]
            except KeyError as KeyExc:
                print(KeyExc)
    
    def investment_costs(self):
        """calculates the investment costs

        Returns:
            float: investment costs per year
        """
        inv_cost = self.PVCOSTS * self.ROOFSIZE
        inv_cost += self.MOUNTINGCOSTS * self.ROOFSIZE
        inv_cost += self.CONNECTIONCOSTS
        inv_cost += self.ADDITIONALCOSTS
        
        return inv_cost
    
    def running_costs(self):
        """calculates the running costs

        Returns:
            float: running costs per year
        """
        run_cost = (self.get_data_for_house('E_y') * self.ENERGYPRICE) * self.SHARE
        
        return run_cost
    
    def calculate_profit(self):
        """calculate the profit which is the sales from selling power to the grid minus the "Pachtgebuehren"

        Returns:
            float: profit
        """
        profit = (self.get_data_for_house('E_y') * self.ENERGYPRICE) - self.running_costs()
        
        return profit