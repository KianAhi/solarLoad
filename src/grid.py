import hydrogenStorage
import house
from datetime import date
from calendar import monthrange

class electricalGrid:
    def __init__(self):
        self.hydrogenStorage = hydrogenStorage.hydrogenStorage()
        self.houses = []
        #? IDEA:
        #? dictionary with the format:
        #? {hour: {inputs: xxx, outputs: xxx, netto: xxx, autarky: xxx}}
        #? can be split into np arrays for further plotting etc. easily
        self.time = {}
    
    def add_house(self, yaml_path=None, index="default"):
        """adds a house to the list of houses of the electricalGrid class

        Args:
            yaml_path (str, optional): if supplied: special yaml file for the house data. Defaults to None.
            index (str, optional): if supplied: loads the yaml data from the file at this index. Defaults to "default".
        """
        self.houses.append(house.House(yaml_path=yaml_path, index=index))
    
    def calculate_investment_costs(self):
        inv_costs = self.hydrogenStorage.calculate_investment_costs()
        for house in self.houses:
            inv_costs += house.calculate_investment_costs()
        
        return inv_costs
    
    def simulate_houses(self):
        """simply simulate every house (sequentially -> we do not go over the API limit)
        """
        for house in self.houses:
            house.daily_power()
            house.simulate_daily()


def model1(houses, hydrogenStorage, startDate = date(2020,1,1), endDate = date(2020,12,31)):
    """Simulate the first case: House Owner lives in own house and prioritses the usage of the generated energy over stored energy

    Args:
        houses (list): list that holds all the instances of the house class
        hydrogenStorage (obj): Hydrogen storage object, holds the amount of stored hydrogen
        startDate (datetime.date, optional): Starting date for the simulated time-frame Defaults to date(2020,1,1).
        endDate (datetime.date, optional): Ending date for the simulated time-frame Defaults to date(2020,12,31).

    Returns:
        houses, hydrogenStorage
    """
    accumulatorStorage = 0
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    hours = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    years = []
    for i in range(endDate.year - startDate.year + 1):
        years.append(startDate.year + i)
        
    pv_dict = {}
    for year in years:
        for month in months:
            _, days = monthrange(year, months.index(month)+1)
            for day in range(1,days+1):
                for hour in hours:
                    for house in houses:
                        nettoValue = house.pvNetto[year][month][day][hour]
                        if nettoValue > 0: # reinschieben in speicher oder 
                            if house.accumulatorStorage < house.accumulatorCap:
                                if house.accumulatorStorage + nettoValue > house.accumulatorCap:
                                    diff = house.accumulatorCap - house.accumulatorStorage
                                    house.accumulatorStorage = house.accumulatorCap
                                    hydrogenStorage.input(nettoValue - diff)
                                else:
                                    house.accumulatorStorage += nettoValue
                            else:
                                hydrogenStorage.input(nettoValue)
                        else: # alles benutzt
                            energyDiff = abs(nettoValue)
                            if energyDiff - house.accumulatorStorage > 0:
                                energyDiff -= house.accumulatorStorage
                                house.accumulatorStorage = 0
                            else:
                                house.accumulatorStorage -= energyDiff
                                energyDiff = 0
                            if energyDiff - hydrogenStorage.effective_output_capacity  > 0:
                                energyDiff -= hydrogenStorage.effective_output_capacity 
                                hydrogenStorage.output(hydrogenStorage.effective_output_capacity)
                            else:
                                hydrogenStorage.output(energyDiff)
                                energyDiff = 0
                            if energyDiff > 0:
                                house.gridUsage(energyDiff)
                                energyDiff = 0
                        
    return houses, hydrogenStorage 



if __name__ == "__main__":
    storage = hydrogenStorage.hydrogenStorage()
    model1()