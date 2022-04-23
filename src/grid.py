import hydrogenStorage
from datetime import date
from calendar import monthrange

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