def model1(pvIn, customerUsage, accumulatorCap, hydrogenStorage):
    # Average hourly data over one year
    #pvIn
    #customerUsage
    accumulatorStorage = 0


    for month in months:
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
                        if energyDiff - (hydrogenStorage.currentHydrogen * hydrogenStorage.Hydrogen_to_Electricity_efficiancy )  > 0:
                            energyDiff -= hydrogenStorage.currentHydrogen * hydrogenStorage.Hydrogen_to_Electricity_efficiancy 
                            hydrogenStorage.currentHydrogen = 0## TODO hydrogen rausnehmen mit wirkungsgrad
                        else:
                            hydrogenStorage.currentHydrogen * (1 / hydrogenStorage.hydrogen_to_Electricity_fficiancy) -= energyDiff
                            energyDiff = 0
                        if energyDiff > 0:
                            house.gridUsage(energyDiff)
                            energyDiff = 0
                        
                        


if __name__ == "__main__":
    storage = hydrogenStorage()
    model1()