#!/usr/bin/env python
# coding: utf-8

print("CapstoneCode.py has been called")
import numpy as np
from scipy.optimize import brute
import csv
import random
import matplotlib.pyplot as plt
import copy
import math
import pandas as pd
from os.path import isfile
import sys

# Check if the correct number of arguments is provided from user input
if len(sys.argv) != 9:
    print("Usage: python script.py <parkingLotSize> <rebatePercent> <markup> <weeks> <installCost> <marketPrice> <hydroPrice> <seasonality>")
    sys.exit(1)

# Parse command-line arguments
parkingLotSize = int(sys.argv[1])
rebatePercent = float(sys.argv[2])
markup = float(sys.argv[3])
weeks = int(sys.argv[4])
installCost = float(sys.argv[5])
marketPrice = float(sys.argv[6])
hydroPrice = float(sys.argv[7])
seasonality = float(sys.argv[8])

# # Data
# Open the CSV file
csv_file = open('time_demand.csv', 'r')
csv_file2 = open('vehicle_registration_2022.csv', 'r')
csv_file3 = open('rebates.csv', 'r')

# Create a csv.reader object
csv_reader = csv.reader(csv_file)
csv_reader2 = csv.reader(csv_file2)
csv_reader3 = csv.reader(csv_file3)

# Initialize an empty array to store the CSV data
data_array = []
data_array2 = []
data_array3 = []

# Read and store data row by row
for row in csv_reader:
    data_array.append(row)
for row in csv_reader2:
    data_array2.append(row)
for row in csv_reader3:
    data_array3.append(row)

# Close the CSV file
csv_file.close()
csv_file2.close()
csv_file3.close()

demandHourly = [item for sublist in [row[1:] for row in data_array[1:-1]] for item in sublist]
vehicleRegistration2022 = data_array2
rebates = data_array3

# # Model functions
#Need a script that calculates percent of vehicles in area that are EVs based on vehicle registration data
#Defines variable percentEV

# Specify the column index you want to analyze
column_index = 3  # 3 corresponds to EV included
target_text = "Yes"
count_matches = 0

# Iterate through the rows and check for matches
for row in vehicleRegistration2022[1:]:  # Skip the header row
    if row[column_index] == target_text:
        count_matches += 1

# Calculate the percentage
total_rows = len(vehicleRegistration2022) - 1  # Subtract 1 to exclude the header row
percentEV = count_matches / total_rows

def chargingDemand(demandHourly,percentEV,chargerCount,parkingLotSize):
    #Takes inputs: array demandHourly which is 13 (hours per day) by 7 (days per week), float percentEV, float chargingProbability
    #Returns total number of charging instances per week weeklyChargeCount
    
    chargerCount = round(chargerCount)
    weeklyChargeCount = 0
    randomCarArray = []
    chargers = [[False,"",""]]*chargerCount
    chargersFilled = [chargers]
    falses = []
    chargersOccupied = 0
    for i in demandHourly:
        
        parkingSpots = [False,"",""]*(173 - chargerCount)
        chargers = sorted(chargers, key=lambda x: not x[0])
        
        #Cars leaving/staying at chargers:
        for k, car in enumerate(chargers):
            if car[0] and car[2] >= 100:
                chargers[k] = [False,"",""]
                chargersOccupied -= 1
            #ASSUMING CAR CHARGES TO 100%
            elif car[0] and car[2] < 100:
                #car will charge (ASSUMING 20% PER HOUR - CORRECT LATER)
                chargers[k][2] += 20
                
        #Sort chargers so filled comes first
        chargers = sorted(chargers, key=lambda x: not x[0])
                
        for j, car in enumerate(parkingSpots):
            randomCar = generateCar(float(i),percentEV)
            randomCarArray.append(randomCar)
            #if random car is EV that wants to charge:
            if randomCar[1] and randomCar[2] < 40 and chargersOccupied < chargerCount:
                #car will charge (ASSUMING 20% PER HOUR - CORRECT LATER)
                randomCar[2] += 20
                #car parks in charger spot
                chargers = sorted(chargers, key=lambda x: not x[0])
                chargers[chargersOccupied] = randomCar
                chargersOccupied += 1
            else:
                #car parks in regular spot
                parkingSpots[j] = randomCar
                
        chargersFilled.append(copy.deepcopy(chargers))
        
        weeklyChargeCount += chargersOccupied
    return(weeklyChargeCount,chargersFilled)

def generateCar(demand,percentEV):
    #generates a Car: array of length 3 [does the car exist?,is the car an EV?,SOC]
    #to do: add additional car properties
    #if the spot is empty (random number is above % chance that spot is filled)
    car = [False,"",""]
    if random.randint(1, 100) > (demand*100):
        return car
    #if car is EV
    elif random.randint(1, 100) < (percentEV*100):
        car[0] = True
        car[1] = True
        car[2] = random.randint(20, 80)
    else:
        car[0] = True
        car[1] = False
    
    return car

chargingDemand(demandHourly,percentEV,3,parkingLotSize)[0]

def powerToHour(markup,power,hydroPrice):
    #Calculates the price per hour based on price per kWh
    markupHour = markup*power #$/kWh * kW = $/h
    priceHour= (hydroPrice+markup)*power
    return(priceHour,markupHour)


# #NOTE: Charger quote is from Chargepoint and is currently hardcoded into the function below (change this later):
def profit(installCost,rebatePercent,weeks,demandHourly,percentEV,chargers,parkingLotSize,hydroPrice,marketPrice,markup,power):
    #Takes inputs: float installCost in CAD, float rebatePercent, chargeCharge in CAD/hour (change this eventually to CAD/kWh and weeklyChargeCount to kwH/week)
    #plus params for ChargingDemand
    hourlyPrice = powerToHour(markup,power,hydroPrice)[0]
    hourlyProfit = powerToHour(markup,power,hydroPrice)[1]
    if marketPrice < hourlyPrice:
        demandScale = marketPrice/hourlyPrice
    else:
        demandScale = 1
    
    revenue = 0
    revenueWeekly = []
    if power <= 7.2:
        chargerCost = 11500
    elif 7.2 < power <= 20:
        chargerCost = 18000
    else:
        chargerCost = 100000
    costsBeforeRebate = (installCost+chargerCost)*chargers
    [rebateAmount,rebateMax] = rebate(float(power))
    if costsBeforeRebate*(1-rebateAmount) > rebateMax:
        costs = costsBeforeRebate-(rebateMax*rebatePercent)
    else:
        rebateAmount = 1-((1-rebateAmount)*rebatePercent)
        costs = costsBeforeRebate * rebateAmount
    #This needs to be adjusted for inflation later
    #efficiency
    demand = np.mean([chargingDemand(demandHourly,percentEV,chargers,parkingLotSize)[0] for i in range(5)])
    while weeks > 0:
        weekRevenue = demand* hourlyProfit * demandScale
        if (weeks/52 % 1)*52 < 35:
            weekRevenue *= seasonality #Winter scaling factor
        revenue += weekRevenue
        revenueWeekly.append(revenue)
        weeks -= 1
    return(revenue-costs,revenueWeekly,costs,costsBeforeRebate)
    #Returns total profit/loss in CAD

def rebate(power):
    #Based on charger power, returns maximum rebate percentage and maximum rebate in dollars
    percentPaid = 1
    rebateMax = 0
    usedRebate = ""
    for i in rebates[1:]:
        if i[0] != usedRebate and (float(i[1]) >= float(power)) and (float(power) <= float(i[2])):
            usedRebate = i[0]
            percentPaid *= (1-float(i[3]))
            rebateMax += float(i[4])
    return(percentPaid,rebateMax)

def chargerSizing(installCost,rebatePercent,weeks,demandHourly,percentEV,parkingLotSize,hydroPrice,marketPrice,markup):
    #This is an optimization function that finds the optimal number of chargers to maximize profit

    def profitMin(vars):
        x, y = vars
        return(-profit(installCost,rebatePercent,weeks, demandHourly,percentEV,x,parkingLotSize,hydroPrice,marketPrice,markup, y)[0])
    
    # Define the ranges for each parameter
    param_ranges = (slice(2, 16, 2), slice(7.2, 100, 6.4))  # Example ranges, adjust as needed

    # Use brute force to minimize the profit function
    result = brute(profitMin, param_ranges, full_output=True, finish=None)

    chargers = result[0][0]
    power = result[0][1]
    netprofit = -result[1]
    return(chargers, power)

def EVDemandIncrease(markup,chargers):
    #returns the % increase in EV sales given electricity price markup and number of chargers installed
    coeffs = {
        1:[0.1997,-0.032]
        ,2:[0.1997,-0.032]
        ,3:[0.1997,-0.032]
        ,4:[0.2193,-0.031]
        ,5:[0.2193,-0.031]
        ,6:[0.2193,-0.031]
        ,7:[0.227,-0.028]
        ,8:[0.227,-0.028]
        ,9:[0.227,-0.028]
        ,10:[0.2325,-0.027]
        ,11:[0.2325,-0.027]
        ,12:[0.236,-0.026]
        ,13:[0.236,-0.026]
        ,14:[0.2405,-0.025]
        ,15:[0.2405,-0.025]
        ,16:[0.2405,-0.025]
    }
    if coeffs[chargers][0]*math.exp(coeffs[chargers][1]*markup) < 0.16:
        increase = 0.1
    else:
        increase = coeffs[chargers][0]*math.exp(coeffs[chargers][1]*markup) - 0.16
    return(increase*100)

# Carbon emissions Model------------------------------------------------------------------------------------
#INPUTS
#Average kilometers driven per year in BC is 13,100kms
kmDriven = 13100
evSales = 18 #Percent, From https://dailyhive.com/vancouver/bc-electric-vehicle-sales-uptake-2022-statistics

def GHG_emissions(percentEVSales, numberOfChargers):
    Vehicles = pd.read_csv('Copy of Vehicle Population - 2022 Passenger Vehicles_Full _data.csv')
    EmissionsFactors = pd.read_csv('EmissionsFactorsTechscape.csv')
    SizeMap = pd.read_csv('SizeMap.csv')
    vehicleSales2022 = pd.read_csv('ev_sales_2022.csv')

    # Q4 2022 car sales in BC
    carSales = int(vehicleSales2022.query("Month=='Total'")["Unit Sales"].iloc[0])
    bcPopulationPercent = 662248 / 39498018  # Vancouver pop / canada pop
    #Removed BC population 5403528 replaced with Vancouver
    vanCarSales = math.ceil(carSales * bcPopulationPercent)

    #Need to calculate baseline % of vehicles that are EV/gas
    #Then use study values to get % increase/decrease for 2035
    isEV_counts = Vehicles['Electric Vehicle Included'].value_counts()
    percentReplaced = vanCarSales/sum(isEV_counts)
    percentageEV = (isEV_counts['Yes'] / len(Vehicles)) * 100
    percentageICE = 100 - percentageEV
    salesIncreasePerYear = (100-18)/(2035-2023) #Assuming increase in EV purchases is linear and 100% of new purchases are EVs by 2035
    percentageEV2035 = percentageEV
    for i in range(2035-2023):
        if percentageEV2035 < 100:
            percentageEV2035 = percentReplaced * (evSales + i*salesIncreasePerYear) + (1-percentReplaced) * percentageEV2035
        else:
            pass
    percentageICE2035 = 100 - percentageEV2035
    ICEadjustmentFactor2035 = percentageICE2035/percentageICE
    EVadjustmentFactor2035 = percentageEV2035/percentageEV

    #Gas vehicles baseline
    VehiclesMapped = Vehicles.merge(SizeMap, on='Body Style', how='left')
    GasVehiclesEmissions = VehiclesMapped.merge(EmissionsFactors[EmissionsFactors['Powertrain type'] == 'Gasoline'], on='Size', how='left')
    GasVehiclesEmissions = GasVehiclesEmissions[GasVehiclesEmissions['Electric Vehicle Included'] == 'No']
    GasBaselineEmissions_WTP = GasVehiclesEmissions.groupby('Size')['Well to pump emissions (g/km)'].sum().reset_index()
    GasBaselineEmissions_PTW = GasVehiclesEmissions.groupby('Size')['Pump to wheel emissions (g/km)'].sum().reset_index()
    GasBaselineEmissions_WTP2035 = GasBaselineEmissions_WTP['Well to pump emissions (g/km)'] * ICEadjustmentFactor2035
    GasBaselineEmissions_PTW2035 = GasBaselineEmissions_PTW['Pump to wheel emissions (g/km)'] * ICEadjustmentFactor2035

    #EVs Baseline
    EVBaselineEmissions = VehiclesMapped.merge(EmissionsFactors[EmissionsFactors['Powertrain type'] == 'EV'], on='Size', how='left')
    EVBaselineEmissions = EVBaselineEmissions[EVBaselineEmissions['Electric Vehicle Included'] == 'Yes']
    EVBaselineEmissions_WTP = EVBaselineEmissions.groupby('Size')['Well to pump emissions (g/km)'].sum().reset_index()
    EVBaselineEmissions_PTW = EVBaselineEmissions.groupby('Size')['Pump to wheel emissions (g/km)'].sum().reset_index()

    EVBaselineEmissions_WTP2035 = EVBaselineEmissions_WTP['Well to pump emissions (g/km)'] * EVadjustmentFactor2035
    EVBaselineEmissions_PTW2035 = EVBaselineEmissions_PTW['Pump to wheel emissions (g/km)'] * EVadjustmentFactor2035

    #Baseline in one dataframe (g/km driven)
    BaselineEmissions = pd.concat([GasBaselineEmissions_WTP,
                                GasBaselineEmissions_PTW['Pump to wheel emissions (g/km)'],
                                GasBaselineEmissions_WTP2035, GasBaselineEmissions_PTW2035,
                                EVBaselineEmissions_WTP['Well to pump emissions (g/km)'], EVBaselineEmissions_PTW['Pump to wheel emissions (g/km)'],
                                EVBaselineEmissions_WTP2035, EVBaselineEmissions_PTW2035], axis = 1)
    BaselineEmissions.columns = ['Size', 'Gas WTP', 'Gas PTW', 'Gas WTP 2035', 'Gas PTW 2035', 'EV WTP', 'EV PTW', 'EV WTP 2035', 'EV PTW 2035']
    BaselineEmissions

    #Project Emissions
    salesIncreasePerYearProject = (100-18+percentEVSales)/(2035-2023)
    percentageEV2035Project = percentageEV
    
    #EV sales impact
    evSalesYearly = []
    for i in range(2035-2023):
        if percentageEV2035Project < 100:
            percentageEV2035Project = percentReplaced * (evSales + i*salesIncreasePerYearProject) + (1-percentReplaced) * percentageEV2035Project
            evSalesYearly.append(percentageEV2035Project)
        else:
            evSalesYearly.append(percentageEV2035Project)
            pass
    percentageICE2035Project = 100 - percentageEV2035Project
    ICEadjustmentFactor2035Project = percentageICE2035Project/percentageICE
    EVadjustmentFactor2035Project = percentageEV2035Project/percentageEV
    
    #Gas vehicles project
    GasProjectEmissions_WTP2035 = GasBaselineEmissions_WTP['Well to pump emissions (g/km)'] * ICEadjustmentFactor2035Project
    GasProjectEmissions_PTW2035 = GasBaselineEmissions_PTW['Pump to wheel emissions (g/km)'] * ICEadjustmentFactor2035Project

    #EVs project
    EVProjectEmissions_WTP2035 = EVBaselineEmissions_WTP['Well to pump emissions (g/km)'] * EVadjustmentFactor2035Project
    EVProjectEmissions_PTW2035 = EVBaselineEmissions_PTW['Pump to wheel emissions (g/km)'] * EVadjustmentFactor2035Project

    #Charger lifecycle project
    chargerLifecycle = 4737.6 + 71.0 + 86.3 + 3310.7 #Production, transportation, installation, and recycling in kg CO2
    totalChargerEmissions = numberOfChargers * chargerLifecycle #in kg CO2
    totalChargerEmissions

    #TOTAL

    totalBaseline = (sum(EVBaselineEmissions_WTP2035) + sum(EVBaselineEmissions_WTP2035) + sum(GasBaselineEmissions_WTP2035) + sum(GasBaselineEmissions_PTW2035))*13100/1000
    totalProject = (sum(EVProjectEmissions_WTP2035) + sum(EVProjectEmissions_WTP2035) + sum(GasProjectEmissions_WTP2035) + sum(GasProjectEmissions_PTW2035))*13100/1000
    netCarbon = (-totalProject - totalChargerEmissions + totalBaseline)/1000     # CO2 reduction (CO2)
    return (netCarbon,[percentageEV,evSalesYearly[-1]],[percentageEV,percentageEV2035])


# Export data to Excel file
optimal = chargerSizing(installCost,rebatePercent,weeks,demandHourly,percentEV,parkingLotSize,hydroPrice,marketPrice,markup)

# Specify the file name for outputting results
file_name = "Power BI Data - DO NOT TOUCH.xlsx"

# Append the optimal # of chargers & charger power at the end
options = [[2,7.2],[2,20]
          ,[4,7.2],[4,20]
          ,[6,7.2],[6,20]
          ,[8,7.2],[8,20],list(optimal)]

data_exist = False
# Read existing data in Excel if file exists
if isfile(file_name):
    excel = pd.ExcelFile(file_name)
    existingData_summary = pd.read_excel(excel, 'Summary', index_col=None)
    existingData_profit = pd.read_excel(excel, 'Profit over time', index_col=None)
    data_exist = True

chargers = []
power = []
unique_id = []
weekNumber = []
totalProfit = []
weeklyProfit = []
costAfterRebate = []
costBeforeRebate = []
netCarbon = []

for i in options:
    chargers.append(i[0])
    power.append(i[1])
    unique_id.append(f"{i[0]}c{i[1]}kW{rebatePercent}%{markup}$")
    weekNumber.extend(range(1,weeks+1))
    percentEVSales = EVDemandIncrease(markup,i[0])
    numberOfChargers = i[0]
    netCarbon.append(GHG_emissions(percentEVSales, numberOfChargers)[0])
    revenueData = profit(installCost,rebatePercent,weeks,demandHourly,percentEV,i[0],parkingLotSize,hydroPrice,marketPrice,markup,i[1])
    totalProfit.append(revenueData[0])
    weeklyProfit.extend(revenueData[1])
    costAfterRebate.append(revenueData[2])
    costBeforeRebate.append(revenueData[3])

# We're going to have the same unique id, charger number and power for all listed weeks in the profit tab
# These values will change every 522 rows, so reorganize lists to reflect this pattern
duplicateValues = list(np.ones(len(options), dtype=int)*weeks)
unique_id_profit = [x for x, number in zip(unique_id, duplicateValues) for _ in range(number)]
chargers_profit = [x for x, number in zip(chargers, duplicateValues) for _ in range(number)]
power_profit = [x for x, number in zip(power, duplicateValues) for _ in range(number)]
optimal_summary = ["No" for i in range(len(unique_id))]
optimal_summary[-1] = "Yes"

# Create dataframe for the weekly profit tab
profitData = {}
profitData["Unique ID"] = unique_id_profit
profitData["Number of chargers"] = chargers_profit
profitData["Power"] = power_profit
profitData["Week"] = weekNumber
profitData["Profit"] = weeklyProfit
weeklyExcel = pd.DataFrame(profitData).reset_index()

# Create dataframe for the summary tab
summaryData = {}
summaryData["Unique ID"] = unique_id
summaryData["Number of chargers"] = chargers
summaryData["Power"] = power
summaryData["Total profit"] = totalProfit
summaryData["Cost after Rebates"] = costAfterRebate
summaryData["Cost before Rebates"] = costBeforeRebate
summaryData["Rebate %"] = list(np.ones(len(unique_id))*rebatePercent)
summaryData["Markup"] = list(np.ones(len(unique_id))*markup)
summaryData["Optimal?"] = optimal_summary
summaryData["CO2 reduction"] = netCarbon
summaryExcel = pd.DataFrame(summaryData).reset_index()

if data_exist:
    common_ids = pd.merge(summaryExcel, existingData_summary, on="Unique ID", how='inner')["Unique ID"]
    existingData_summary_filtered = existingData_summary[~existingData_summary["Unique ID"].isin(common_ids)]
    existingData_profit_filtered = existingData_profit[~existingData_profit["Unique ID"].isin(common_ids)]
    weeklyExcel = pd.concat([existingData_profit_filtered, weeklyExcel], ignore_index=True)
    summaryExcel = pd.concat([existingData_summary_filtered, summaryExcel],)

# Populate the Excel file with the dataframes defined earlier
with pd.ExcelWriter(file_name) as excelFile:
    summaryExcel.to_excel(excelFile, sheet_name='Summary', index=False)
    weeklyExcel.to_excel(excelFile, sheet_name='Profit over time', index=False)

print(f"The data has been written to {file_name}.")