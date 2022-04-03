import requests

class PVGIS:
    def __init__(self, version='5.2', tool_name="PVcalc"):
        self.base_url = self.pvgis_url(version)
        self.tool = self.check_tool_name(tool_name)
        self.data = None
        # format: key -> list of possible types, bool for obligatory value, default value (if None and obligatory = True -> raise Error), possible values (if exist)
        self.api_inputs = {
            "lat": [float, True, None],
            "lon": [float, True, None],
            "usehorizon": [[int, list], False, 1, [0, 1]],
            "raddatabase": [str, False, "PVGIS-SARAH", ["PVGIS-SARAH", "PVGIS-NSRDB", "PVGIS-ERA5", "PVGIS-COSMO"]],
            "peakpower": [float, True, None],
            "pvtechchoice": [str, False, "crystSi", ["crystSi", "CIS", "CdTe", "Unknown"]],
            "mountingplace": [str, False, "free", ["free", "building"]],
            "loss": [float, True, 14.0],
            "fixed": [int, False, 1],
            "angle": [float, False, 0],
            "aspect": [float, False, 0],
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
            "browser": [int, False, 0]
        }
        
    def pvgis_url(self, version):
        if version == "5.1":
            return "https://re.jrc.ec.europa.eu/api/v5_1/"
        elif version == "5.2":
            return "https://re.jrc.ec.europa.eu/api/v5_2/"
        else:
            raise ValueError("PVGIS only supports version 5.1 and 5.2! You have given version %s" % version)
    
    def check_tool_name(self, tool_name):
        if tool_name in ["PVcalc", "SHScalc", "MRcalc", "DRcalc", "seriescalc", "tmy", "printhorizon"]:
            return tool_name
        else:
            raise ValueError("%s is not a correct tool name for use with PVGIS!")
    
    def set_value(self, key, value):
        try:
            if isinstance(value, self.api_inputs[key][0]):
                self.api_inputs[key][2] = value
                self.api_inputs[key][1] = True
            else:
                raise ValueError("%s is not of type %s" % (value, self.api_inputs[key][0]))
        except KeyError:
            raise KeyError("%s is not a key of api_inputs!" % key)
    
    def generate_api_string(self):
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
        api_request_url = self.generate_api_string()
        r = requests.get(api_request_url)
        self.data = r.json()
    
    def get_data(self, print_output=False):
        data_list = []
        for variable in self.data['outputs']['totals']['fixed']:
            numerical_data = self.data['outputs']['totals']['fixed'][variable]
            numerical_unit = self.data['meta']['outputs']['totals']['variables'][variable]['units']
            data_description = self.data['meta']['outputs']['totals']['variables'][variable]['description']
            data_list.append([variable, str(numerical_data) + " " + numerical_unit, data_description])
        
        if print_output:
            for dp in data_list:
                print("%s = %s "% (dp[0], dp[1]))
                print(dp[2] + "\n---")
        
        return data_list

if __name__ == "__main__":
    test = PVGIS()
    test.set_value("lat", 49.357)
    test.set_value("lon", 6.725)
    test.set_value("peakpower", 1.0)
    test.set_value("optimalinclination", 1)
    test.set_value("optimalangles", 1)
    test.send_api_request()
    data = test.get_data(print_output=True)