import hydrogenStorage
import house
import datetime
from datetime import date, timedelta
from datetime import date
from calendar import monthrange
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateFormatter, AutoDateLocator
import numpy as np
import random

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
        ##TODO: Can we do the costs in a list for every month? Then we would see whenever we add a house after x months how the costs go up
        inv_costs = self.hydrogenStorage.calculate_investment_costs()
        for house in self.houses:
            inv_costs += house.calculate_investment_costs()
        
        return inv_costs
    
    def calculate_revenue(self, startDate, endDate):

        for house in self.houses:
            house.calculate_monthly_revenue()

        labels = []
        revenue = []
        for month in self.months_between(startDate, endDate):
            month = month.strftime("%Y-%m")
            labels.append(month)
            solarRevenue = 0
            hydroRevenue = 0
            batteryRevenue = 0
            for house in self.houses:
                try:
                    solarRevenue += house.monthlyRevenue[month]["solar"]
                    hydroRevenue += house.monthlyRevenue[month]["hydro"]
                    batteryRevenue += house.monthlyRevenue[month]["accumulator"] 
                except KeyError:
                    pass
            revenue.append([solarRevenue, hydroRevenue, batteryRevenue])
        return revenue, labels


    def months_between(self, start_date, end_date):

        if start_date > end_date:
            raise ValueError(f"Start date {start_date} is not before end date {end_date}")

        year = start_date.year
        month = start_date.month

        while (year, month) <= (end_date.year, end_date.month):
            yield datetime.date(year, month, 1)
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1  


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
            todaysDate = startDate + timedelta(days=day)
            month = todaysDate.month #! Added this so we can use todays date further down for tracking purposes
            #month = (startDate + datetime.timedelta(days=day)).month
            for hour in range(24):
                #print("It is day #%s and hour %s:00" % (day+1, hour))
                current_hour = hour + day*len(range(24))
                avg_autarky = 0
                avg_nettoValue = 0
                for house in self.houses:
                    house_autarky = 0
                    #1 calculate production and consumption at every hour
                    #2 calculate the nettoValue
                    production = random.uniform(0.975, 1.025) * house.pv_daily[month][hour][1]
                    consumption = random.uniform(0.975, 1.025)* house.daily_consumption[hour][1]
                    nettoValue = production - consumption
                    avg_nettoValue += nettoValue

                    if nettoValue > 0: # reinschieben in speicher oder 
                        house.energyUsage(hour, consumption, todaysDate, energy_type = "solar")
                        if house.accumulatorStorage < house.accumulatorCap:
                            if house.accumulatorStorage + nettoValue > house.accumulatorCap:
                                diff = house.accumulatorCap - house.accumulatorStorage
                                house.accumulatorStorage = house.accumulatorCap
                                self.hydrogenStorage.input(nettoValue - diff)
                                house_autarky = 1
                            else:
                                house.accumulatorStorage += nettoValue
                                house_autarky = 1
                        else:
                            self.hydrogenStorage.input(nettoValue)
                            house_autarky = 1
                    else: # alles benutzt
                        house.energyUsage(hour, production, todaysDate, energy_type = "solar")
                        energyDiff = abs(nettoValue)
                        if energyDiff - house.accumulatorStorage > 0:
                            energyDiff -= house.accumulatorStorage
                            house.energyUsage(hour, house.accumulatorStorage, todaysDate, energy_type = "accumulator")
                            house.accumulatorStorage = 0
                        else:
                            house.accumulatorStorage -= energyDiff
                            house.energyUsage(hour, energyDiff, todaysDate, energy_type = "accumulator")
                            energyDiff = 0
                            house_autarky = 1
                        if energyDiff - self.hydrogenStorage.effective_output_capacity  > 0:
                            energyDiff -= self.hydrogenStorage.effective_output_capacity 
                            house.energyUsage(hour, self.hydrogenStorage.effective_output_capacity, todaysDate, energy_type = "hydro")
                            self.hydrogenStorage.output(self.hydrogenStorage.effective_output_capacity)
                        else:
                            self.hydrogenStorage.output(energyDiff)
                            house.energyUsage(hour, energyDiff, todaysDate, energy_type = "hydro")
                            energyDiff = 0
                            house_autarky = 1
                        if energyDiff > 0:
                            house_autarky = energyDiff/abs(nettoValue)
                            house.energyUsage(hour, energyDiff, todaysDate, energy_type = "grid")
                            energyDiff = 0
                    avg_autarky += house_autarky
                # at the first hour (index = 0) the energyState is just the nettoValue
                # else: successive addition of nettoValue to energyState of an hour before
                if current_hour != 0:
                    self.energyState.append(self.energyState[current_hour-1] + avg_nettoValue/len(self.houses))
                else:
                    self.energyState.append(avg_nettoValue/len(self.houses))
                self.H2storage.append(self.hydrogenStorage.effective_output_capacity)
                self.autarky.append(avg_autarky/len(self.houses))


    def getyLabelSpaced(self,startDate, endDate):
        max_hour = (endDate - startDate).total_seconds() / 3600
        hour = 0.0
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
        return ticks, labels
    def plots(self, startDate = date(2020,8,1), endDate = date(2022,8,1)):
        """TODO
        Subplot1: h2Storage over time
        Subplot1: energyState over time
        Subplot1: bought energy from provider over time
        Subplot2: autarky over time
        Subplot3: cost, revenue, profit over time
        """
        
        for h in self.houses:
            print(h.calculate_investment_costs())
        
        revenue, labels = self.calculate_revenue(startDate,endDate)

        ticks, labels = self.getyLabelSpaced(startDate,endDate)   

        fig, (ax1, ax2, ax3) = plt.subplots(3,1)
        

        ax1.set_title="H2 storage, energyState over time"
        ax1.plot(np.linspace(0,len(self.H2storage)-1, len(self.H2storage)), np.array(self.H2storage))
        ax1.plot(np.linspace(0,len(self.energyState)-1, len(self.energyState)), np.array(self.energyState))
        ax1.set_ylabel('Energy [kWh]')
        #ax1.set_xlabel('Time [months]')
        ax1.set_xticks(ticks, labels)
        ax1.legend(["H2 storage", "Energy State"])

        ax2.set_title="Autarky over time"
        ax2.plot(np.linspace(0,len(self.autarky)-1, len(self.autarky)), np.array(self.autarky))
        ax2.sharex = ax1
        ax2.set_xticks(ticks, labels)
        #ax2.set_xlabel('Time [months]')
        ax2.legend(["Autarky"])

        #ax3.set_title="Cost, revenue, profit over time"
        #ax3.set_xlabel('Time [months]')
        #ax3.legend(["Cost", "Revenue", "Profit"])
        #ax3.plot(np.linspace(0,len(self.cost)-1, len(self.cost)), np.array(self.cost))

        solar = [item[0] for item in revenue]
        hydro = [item[1] for item in revenue]
        accumulator = [item[2] for item in revenue]
        ax3.bar(labels, solar, width=0.5, color='b', label="Solar")
        ax3.bar(labels, hydro, width=0.5, color='g',bottom=solar, label="Hydro")
        ax3.bar(labels, accumulator, width=0.5, color='r', bottom = hydro, label = "Accumulator")
        ax3.set_ylabel('Revenue [€]')
        #ax3.sharex = ax1
        ax3.legend()
        plt.xticks(rotation=45, ha='right')
        plt.show()


if __name__ == "__main__":
    # storage = hydrogenStorage.hydrogenStorage()
    # model1()
    startDate = date(2020,8,1)
    endDate = date(2022,8,1)
    grid = electricalGrid()
    for i in range(10):
        grid.add_house()
    grid.simulate_houses()
    grid.simulate_grid(startDate = startDate, endDate=endDate)
    grid.plots(startDate = startDate, endDate=endDate)
    