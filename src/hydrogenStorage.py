class hydrogenStorage:
    def __init__(self):
        self.power2H_efficiency = 0.675
        self.H2power_efficiency = 0.5
        self.storage_capacity = 5000 # unit: kWh
        self.stored_power = 0
        self.effective_output_capacity = 0
        
    ##TODO: calculate costs for using the public grid (ca. 2ct/kwh)
    def input(self, input_power):
        self.stored_power += input_power * self.power2H_efficiency
        self.effective_output_capacity = self.stored_power * self.H2power_efficiency
        if self.stored_power > self.storage_capacity:
            self.stored_power = self.storage_capacity
            raise
    
    def output(self, output_power):
        if self.stored_power - (1.0 / self.H2power_efficiency) * output_power > 0: 
            self.stored_power -= (1.0 / self.H2power_efficiency) * output_power
            self.effective_output_capacity = self.stored_power * self.H2power_efficiency
        else:
            self.stored_power = 0
            self.effective_output_capacity = 0
            raise
    
    def printIt(self):
        print("storage capacity = %s" % self.storage_capacity)
        print("stored power = %s" % self.stored_power)
        print("eff_output capacity = %s" % self.effective_output_capacity)