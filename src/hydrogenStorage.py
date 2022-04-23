class hydrogenStorage:
    def __init__(self, energy_capacity = 5000):
        self.power2H_efficiency = 0.675
        self.H2power_efficiency = 0.5
        self.storage_capacity = energy_capacity # unit: kWh
        self.stored_power = 0
        self.effective_output_capacity = 0
        
    ##TODO: calculate costs for using the public grid (ca. 2ct/kwh)
    def input(self, input_power):
        """handles the power input into the H2 storage

        Args:
            input_power (float): power in kW to be converted to H2 with its respective efficiencies
        """
        self.stored_power += input_power * self.power2H_efficiency
        self.effective_output_capacity = self.stored_power * self.H2power_efficiency
        if self.stored_power > self.storage_capacity:
            self.stored_power = self.storage_capacity
            raise
    
    def output(self, output_power):
        """handles the output of power from the H2 storage

        Args:
            output_power (float): power sent from the H2 storage into the grid
        """
        if self.stored_power - (1.0 / self.H2power_efficiency) * output_power > 0: 
            self.stored_power -= (1.0 / self.H2power_efficiency) * output_power
            self.effective_output_capacity = self.stored_power * self.H2power_efficiency
        else:
            self.stored_power = 0
            self.effective_output_capacity = 0
            raise
    
    #TODO find data for investment costs of H2 storage
    def calculate_investment_costs(self):
        inv_costs = self.storage_capacity * 1000 # approx. costs per kWh storage
        return inv_costs
    
    #TODO find data for running costs of H2 storage
    #! I simply set a cost of 1€ per month per kWh, dunno if correct
    def calculate_running_costs(self):
        return self.storage_capacity * 1
    
    def printIt(self):
        print("storage capacity = %s" % self.storage_capacity)
        print("stored power = %s" % self.stored_power)
        print("eff_output capacity = %s" % self.effective_output_capacity)