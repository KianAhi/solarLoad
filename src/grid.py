import hydrogenStorage
import house
import datetime
from datetime import date, timedelta
from datetime import date
from calendar import monthrange
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateFormatter, AutoDateLocator
import numpy as np

class electricalGrid:
    def __init__(self):
        self.hydrogenStorage = hydrogenStorage.hydrogenStorage(energy_capacity=20000)
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
    
    def simulate_grid(self, startDate = date(2020,1,1), endDate=date(2022,1,1)):
        days = (endDate - startDate).days
        self.energyState = []
        self.H2storage = []
        self.autarky = []
        for day in range(days):
            # calculate month bc we need it to search in the daily data from PVGIS
            month = (startDate + datetime.timedelta(days=day)).month
            for hour in range(24):
                print("It is day #%s and hour %s:00" % (day+1, hour))
                current_hour = hour + day*len(range(24))
                avg_autarky = 0
                avg_nettoValue = 0
                for house in self.houses:
                    #1 calculate production and consumption at every hour
                    #2 calculate the nettoValue
                    production = house.pv_daily[month][hour][1]
                    consumption = house.daily_consumption[hour][1]
                    nettoValue = production - consumption
                    avg_nettoValue += nettoValue
                    if nettoValue > 0: # reinschieben in speicher oder 
                        if house.accumulatorStorage < house.accumulatorCap:
                            if house.accumulatorStorage + nettoValue > house.accumulatorCap:
                                diff = house.accumulatorCap - house.accumulatorStorage
                                house.accumulatorStorage = house.accumulatorCap
                                self.hydrogenStorage.input(nettoValue - diff)
                                avg_autarky += 1
                            else:
                                house.accumulatorStorage += nettoValue
                        else:
                            self.hydrogenStorage.input(nettoValue)
                            avg_autarky += 1
                    else: # alles benutzt
                        energyDiff = abs(nettoValue)
                        if energyDiff - house.accumulatorStorage > 0:
                            energyDiff -= house.accumulatorStorage
                            house.accumulatorStorage = 0
                        else:
                            house.accumulatorStorage -= energyDiff
                            energyDiff = 0
                            avg_autarky += 1
                        if energyDiff - self.hydrogenStorage.effective_output_capacity  > 0:
                            energyDiff -= self.hydrogenStorage.effective_output_capacity 
                            self.hydrogenStorage.output(self.hydrogenStorage.effective_output_capacity)
                        else:
                            self.hydrogenStorage.output(energyDiff)
                            energyDiff = 0
                            avg_autarky += 1
                        if energyDiff > 0:
                            avg_autarky += energyDiff/abs(nettoValue)
                            house.gridUsage(current_hour, energyDiff)
                            energyDiff = 0
                
                # at the first hour (index = 0) the energyState is just the nettoValue
                # else: successive addition of nettoValue to energyState of an hour before
                if current_hour != 0:
                    self.energyState.append(self.energyState[current_hour-1] + avg_nettoValue/len(self.houses))
                else:
                    self.energyState.append(avg_nettoValue/len(self.houses))
                self.H2storage.append(self.hydrogenStorage.effective_output_capacity)
                self.autarky.append(avg_autarky/len(self.houses))


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

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def plots(grid, startDate = date(2020,8,1), endDate = date(2022,8,1)):

    fig, ax = plt.subplots()
    ax.plot(np.linspace(0,len(grid.H2storage)-1, len(grid.H2storage)), np.array(grid.H2storage))
    ax.plot(np.linspace(0,len(grid.energyState)-1, len(grid.energyState)), np.array(grid.energyState))
    ax.plot(np.linspace(0,len(grid.autarky)-1, len(grid.autarky)), np.array(grid.autarky))
    #ax.set_xticks(dateHours)
    max_hour = (endDate - startDate).total_seconds() / 3600
    hour = 0.0
    inc = 1
    ticks = [0.0]
    labels = [startDate.strftime('%b %Y')]
    hour = (monthrange(startDate.year, startDate.month)[1] - (startDate.day-1))*24.0
    cur_date = startDate + datetime.timedelta(days=hour/24)
    ticks.append(hour)
    labels.append(cur_date.strftime('%b %Y'))
    while hour < max_hour:
        cur_date += datetime.timedelta(days=monthrange(cur_date.year, cur_date.month)[1])
        hour = (cur_date - startDate).total_seconds() / 3600
        ticks.append(hour)
        labels.append(cur_date.strftime('%b %Y'))
        
    ax.set_xticks(ticks, labels,rotation=45)
    ax.set_xlabel('Time [months]')
    ax.set_ylabel('Energy [kWh]')

    ax.legend(["H2 storage", "Energy State"])
    plt.show()


if __name__ == "__main__":
    # storage = hydrogenStorage.hydrogenStorage()
    # model1()
    grid = electricalGrid()
    for i in range(10):
        grid.add_house()
    grid.simulate_houses()
    grid.simulate_grid(startDate = date(2020,8,1), endDate=date(2022,8,1))
    plots(grid, startDate = date(2020,5,30), endDate=date(2022,8,1))
    