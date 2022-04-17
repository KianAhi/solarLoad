import requests

class PVGIS:
    def __init__(self, version='5.2', tool_name="PVcalc"):
        """initializing the pvgis API object
        
        Args:
            version (str, optional): version of the PVGIS API. Defaults to '5.2'.
            tool_name (str, optional): which tool to use. Defaults to "PVcalc".
        """
        self.base_url = self.pvgis_url(version)
        self.tool = self.check_tool_name(tool_name)
        self.data = None
        # format: key -> list of possible types, bool for obligatory value, default value (if None and obligatory = True -> raise Error), possible values (if exist)
        self.api_inputs = {
            "lat": [float, True, None],
            "lon": [float, True, None],
            "usehorizon": [[int, list], True, 1, [0, 1]],
            "raddatabase": [str, True, "PVGIS-SARAH", ["PVGIS-SARAH", "PVGIS-NSRDB", "PVGIS-ERA5", "PVGIS-COSMO"]],
            "peakpower": [float, True, None],
            "pvtechchoice": [str, False, "crystSi", ["crystSi", "CIS", "CdTe", "Unknown"]],
            "mountingplace": [str, True, "building", ["free", "building"]],
            "loss": [float, True, 14.0],
            "fixed": [int, True, 1],
            "angle": [float, True, None],
            "aspect": [float, True, None],
            "optimalinclination": [int, False, 0],
            "optimalangles": [int, False, 0],
            "inclined_axis": [int, False, 0],
            "inclined_optimum": [int, False, 0],
            "inclinedaxisangle": [float, False, 0],
            "vertical_axis": [int, False, 0],
            "vertical_optimum": [int, False, 0],
            "verticalaxisangle": [float, False, 0],
            "twoaxis": [int, False, 0],
            "pvprice": [int, False, 0],
            "systemcost": [float, False, None],
            "interest": [float, False, None],
            "lifetime": [int, False, 25],
            "outputformat": [str, True, "json"],
            "browser": [int, True, 0]
        }
        
    def pvgis_url(self, version):
        """returns correct api url for supplied version
        
        Args:
            version (string): version
        
        Raises:
            ValueError: if an incorrect version number is supplied raise error
        
        Returns:
            str: api base url
        """
        
        if version == "5.1":
            return "https://re.jrc.ec.europa.eu/api/v5_1/"
        elif version == "5.2":
            return "https://re.jrc.ec.europa.eu/api/v5_2/"
        else:
            raise ValueError("PVGIS only supports version 5.1 and 5.2! You have given version %s" % version)
    
    def check_tool_name(self, tool_name):
        """checks if supplied tool is an option in the PVGIS API
        
        Args:
            tool_name (str): tool name
        
        Raises:
            ValueError: if an incorrect tool name is supplied raise error
        
        Returns:
            str: tool name
        """
        
        if tool_name in ["PVcalc", "SHScalc", "MRcalc", "DRcalc", "seriescalc", "tmy", "printhorizon"]:
            return tool_name
        else:
            raise ValueError("%s is not a correct tool name for use with PVGIS!")
    
    def set_value(self, key, value):
        """simple helper function to get IO with the api_inputs in the object
        
        Args:
            key (str): key of api_inputs
            value (*): value for key in api_inputs
        
        Raises:
            TypeError: if wrong type
            KeyError: if key is not in api_inputs
        """
        
        try:
            if isinstance(value, self.api_inputs[key][0]):
                self.api_inputs[key][2] = value
                self.api_inputs[key][1] = True
            else:
                raise TypeError("%s is not of type %s" % (value, self.api_inputs[key][0]))
        except KeyError:
            raise KeyError("%s is not a key of api_inputs!" % key)
    
    def generate_api_string(self):
        """generates the api string for further use in the api request

        Raises:
            ValueError: checks for unset but mandatory variables

        Returns:
            str: api request url
        """
        
        input_list = []
        inputs_to_set = []
        for input in self.api_inputs:
            if self.api_inputs[input][1] == True and self.api_inputs[input][2] == None:
                inputs_to_set.append(input)
        if len(inputs_to_set) > 0:
            raise ValueError("following inputs have not been set yet:\n%s" % inputs_to_set)
        for input in self.api_inputs:
            if self.api_inputs[input][1] == True and self.api_inputs[input][2] != None:
                input_list.append("%s=%s" % (input, self.api_inputs[input][2]))
            
        return self.base_url + self.tool + '?' + '&'.join(input_list)
    
    def send_api_request(self):
        """sends the api request and saves the returned JSON object in self.data"""
        api_request_url = self.generate_api_string()
        r = requests.get(api_request_url)
        if r.status_code == 400:
            return r.json()['message']
        self.data = r.json()
        return 0
    
    def get_data(self, print_output=False):
        """parses the JSON object which is sent from the API and supplies the user with a selection of the data

        Args:
            print_output (bool, optional): toggle direct printing. Defaults to False.

        Returns:
            dict: dictionary of the parsed JSON data
        """
        
        data_dict = {}
        for variable in self.data['outputs']['totals']['fixed']:
            numerical_data = self.data['outputs']['totals']['fixed'][variable]
            numerical_unit = self.data['meta']['outputs']['totals']['variables'][variable]['units']
            data_description = self.data['meta']['outputs']['totals']['variables'][variable]['description']
            data_dict[variable] = [numerical_data, str(numerical_data) + " " + numerical_unit, data_description]
        
        if print_output:
            for dp in data_dict.keys():
                print("%s = %s "% (dp, data_dict[dp][1]))
                print(data_dict[dp][2] + "\n---")
        
        return data_dict

class PVDaily:
    def __init__(self, version='5.2', tool_name="DRcalc"):
        """initializing the pvgis API object
        
        Args:
            version (str, optional): version of the PVGIS API. Defaults to '5.2'.
            tool_name (str, optional): which tool to use. Defaults to "DRcalc".
        """
        self.base_url = self.pvgis_url(version)
        self.tool = self.check_tool_name(tool_name)
        self.data = None
        # format: key -> list of possible types, bool for obligatory value, default value (if None and obligatory = True -> raise Error), possible values (if exist)
        self.api_inputs = {
            "lat": [float, True, None],
            "lon": [float, True, None],
            "usehorizon": [[int, list], True, 1, [0, 1]],
            "raddatabase": [str, True, "PVGIS-SARAH", ["PVGIS-SARAH", "PVGIS-NSRDB", "PVGIS-ERA5", "PVGIS-COSMO"]],
            "angle": [float, True, None],
            "month": [int, True, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
            "global": [int, True, 1, [0, 1]],
            "aspect": [float, True, None],
            "outputformat": [str, True, "json"],
            "browser": [int, True, 0]
        }
        
    def pvgis_url(self, version):
        """returns correct api url for supplied version
        
        Args:
            version (string): version
        
        Raises:
            ValueError: if an incorrect version number is supplied raise error
        
        Returns:
            str: api base url
        """
        
        if version == "5.1":
            return "https://re.jrc.ec.europa.eu/api/v5_1/"
        elif version == "5.2":
            return "https://re.jrc.ec.europa.eu/api/v5_2/"
        else:
            raise ValueError("PVGIS only supports version 5.1 and 5.2! You have given version %s" % version)
    
    def check_tool_name(self, tool_name):
        """checks if supplied tool is an option in the PVGIS API
        
        Args:
            tool_name (str): tool name
        
        Raises:
            ValueError: if an incorrect tool name is supplied raise error
        
        Returns:
            str: tool name
        """
        
        if tool_name in ["PVcalc", "SHScalc", "MRcalc", "DRcalc", "seriescalc", "tmy", "printhorizon"]:
            return tool_name
        else:
            raise ValueError("%s is not a correct tool name for use with PVGIS!")
    
    def set_value(self, key, value):
        """simple helper function to get IO with the api_inputs in the object
        
        Args:
            key (str): key of api_inputs
            value (*): value for key in api_inputs
        
        Raises:
            TypeError: if wrong type
            KeyError: if key is not in api_inputs
        """
        
        try:
            if isinstance(value, self.api_inputs[key][0]):
                self.api_inputs[key][2] = value
                self.api_inputs[key][1] = True
            else:
                raise TypeError("%s is not of type %s" % (value, self.api_inputs[key][0]))
        except KeyError:
            raise KeyError("%s is not a key of api_inputs!" % key)
    
    def generate_api_string(self):
        """generates the api string for further use in the api request

        Raises:
            ValueError: checks for unset but mandatory variables

        Returns:
            str: api request url
        """
        
        input_list = []
        inputs_to_set = []
        for input in self.api_inputs:
            if self.api_inputs[input][1] == True and self.api_inputs[input][2] == None:
                inputs_to_set.append(input)
        if len(inputs_to_set) > 0:
            raise ValueError("following inputs have not been set yet:\n%s" % inputs_to_set)
        for input in self.api_inputs:
            if self.api_inputs[input][1] == True and self.api_inputs[input][2] != None:
                input_list.append("%s=%s" % (input, self.api_inputs[input][2]))
            
        return self.base_url + self.tool + '?' + '&'.join(input_list)
    
    def send_api_request(self):
        """sends the api request and saves the returned JSON object in self.data"""
        api_request_url = self.generate_api_string()
        r = requests.get(api_request_url)
        if r.status_code == 400:
            return r.json()['message']
        self.data = r.json()
        return 0
    
    def get_data(self):
        """parses the JSON object which is sent from the API and supplies the user with a selection of the data

        Args:
            print_output (bool, optional): toggle direct printing. Defaults to False.

        Returns:
            dict: dictionary of the parsed JSON data
        """
        
        month_dict = {}
        for dp in self.data['outputs']['daily_profile']:
            month = dp['month']
            time = dp['time']
            irradiance = dp['G(i)']
            if month in month_dict.keys():
                print("%s is in %s" % (month, month_dict.keys()))
                month_dict[month].append([time, irradiance])
            else:
                print("%s is NOT in %s" % (month, month_dict.keys()))
                month_dict[month] = [[time, irradiance]]
        
        self.month_dict = month_dict
        return month_dict


if __name__ == "__main__":
    test = PVDaily()
    # test = PVGIS()
    test.set_value("lat", 49.357)
    test.set_value("lon", 6.725)
    # test.set_value("peakpower", 1.0)
    test.set_value("angle", 35.0)
    test.set_value("aspect", 0.0)
    # test.set_value("optimalinclination", 1)
    # test.set_value("optimalangles", 1)
    test.send_api_request()
    # data = test.get_data(print_output=True)