import hydrogenStorage
from datetime import date
from pandas import date_range
from calendar import monthrange

def model1(houses, hydrogenStorage, startDate = date(2020,1,1), endDate = date(2020,12,31)):
    # Average hourly data over one year
    #pvIn
    #customerUsage
    accumulatorStorage = 0


    if len(pvIn) =! 24:
        return "Error: pvIn must be a list of 24 values"
    if len(customerUsage) != 24:
        return "Error: customerUsage must be a list of 24 values"
    
    dates = date_range(startDate, endDate, freq='D').to_list()
    myCal = {}
    for i in range(endDate.year - startDate.year):
        myCal[i] = {}

    calendar = {year: {month: {day: {hour: []}}}}
    for i in dates:
        i = i.strftime("%Y-%m-%d")

    for year in calendar:
        for month in year:
            for day in month:
                for hour in day: # iterate over all 24 hours

                    for house in houses:
                        if house.pvIn[hour] > customerUsage[hour]:
                            if house.accumulatorStorage < house.accumulatorCap:
                                if house.accumulatorStorage + house.pvIn[hour] - house.customerUsage[hour] > house.accumulatorCap:
                                    diff = house.accumulatorCap - house.accumulatorStorage
                                    house.accumulatorStorage = house.accumulatorCap
                                    hydrogenStorage.inpiut(house.pvIn[hour] - house.customerUsage[hour] - diff)
                                else:
                                    house.accumulatorStorage += house.pvIn[hour] - house.customerUsage[hour]
                            else:
                                hydrogenStorage.input(house.pvIn[hour] - house.customerUsage[hour])
                        else:
                            energyDiff = house.customerUsage[hour] - house.pvIn[hour]
                            if energyDiff - house.accumulatorStorage > 0:
                                energyDiff -= house.accumulatorStorage
                                house.accumulatorStorage = 0
                            else:
                                house.accumulatorStorage -= energyDiff
                                energyDiff = 0
                            if energyDiff - hydrogenStorage.currentHydrogen  > 0:
                                energyDiff -= hydrogenStorage.currentHydrogen 
                                hydrogenStorage.currentHydrogen = 0
                            else:
                                hydrogenStorage.currentHydrogen -= energyDiff
                                energyDiff = 0
                            if energyDiff > 0:
                                house.gridUsage(energyDiff)
                                energyDiff = 0
                        
    return houses, hydrogenStorage 



if __name__ == "__main__":
    storage = hydrogenStorage.hydrogenStorage()
    model1()