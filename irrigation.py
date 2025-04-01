"""
CIT 381 - Spring 2025
Nate Brewer
3/31/2025
A program for a smart irrigation system that will turn on an irrigation system based on a few criteria
1. it is not raining currently
2. it has not rained a significant amount the previous day
3. it will not rain a significant amount the next day
Uses https://developer.accuweather.com/ API
"""
import requests
import json
from gpiozero import LED
from time import sleep
import I2C_LCD_driver

API_KEY = 'Hss84uMqyAIkmL4GYiCQqP4BWR3kwVB6'

# Used a LED as it will send the required 3.3v to the relay to switch it open
relay = LED(19)

# Make the LCD screen object
LCD = I2C_LCD_driver.lcd()

#   
#           API FUNCTIONS
#

"""Will recieve a postal code and hit the AcuWeather API to get the data for that location"""
def postalCodeSearch(postalCode, API_KEY):

    URL = f'http://dataservice.accuweather.com/locations/v1/postalcodes/search?apikey={API_KEY}&q={postalCode}&details=true'
    response = requests.get(URL)
    postalData = response.json()

    if response.status_code == 200 and postalData:
        locationKey = postalData[0]["Key"]
        print("Location Key:", locationKey)
        return locationKey
    else:
        print("Response Code: " + str(response.status_code))
        print("Error fetching location key")

    sleep(0.2)
    #print(postalData)

"""Gets the most current conditions for the recieved 'locationKey' recieved"""
def getCurrentConditions(locationKey, API_KEY):
    
    URL = f'http://dataservice.accuweather.com/currentconditions/v1/{locationKey}?apikey={API_KEY}&details=true'
    response = requests.get(URL)
    locationData = response.json()

    if response.status_code == 200 and locationData:
        #print(locationData)
        return locationData
    else:
        print("Response Code: " + str(response.status_code))
        print("Error fetching data")

    sleep(0.2)

"""Will recieve a postal code and hit the AccuWeather API to get the data for that location"""
def getLastDayConditions(locationKey, API_KEY):

    URL = f'http://dataservice.accuweather.com/currentconditions/v1/{locationKey}/historical/24?apikey={API_KEY}&details=true'
    response = requests.get(URL)
    lastDayConditions = response.json()

    if response.status_code == 200 and lastDayConditions:
        #print(lastDayConditions)
        return lastDayConditions
    else:
        print("Response Code: " + str(response.status_code))
        print("Error fetching data")

    sleep(0.2)

"""Will recieve a postal code and hit the AccuWeather API to get the five day forcast for the area"""
def getFiveDayForcast(locationKey, API_KEY):

    URL = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{locationKey}?apikey={API_KEY}&details=true'
    response = requests.get(URL)
    fiveDayForcast = response.json()

    if response.status_code == 200 and fiveDayForcast:
        #print(fiveDayForcast)
        return fiveDayForcast
    else:
        print("Response Code: " + str(response.status_code))
        print("Error fetching data")

    sleep(0.2)

#
#           END API FUNCTIONS
#



#
#           JSON FUNCTIONs
#

"""Saves data to either a pre-existing file or create a new file"""
def saveToJson(data, filename):

    filename = f'{filename}.json'

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f'data saved to {filename}')

"""Opens Json files and will make the data parsable"""
def openJson(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

#
#           END JSON FUNCTIONS
#



#
#           IRRIGATION LOGIC
#
"""Checks the previous day for more than 0.15 inches of percipitation"""
def previousDayHasSignificantRain():

    previousDay = openJson('last_day_conditions.json')

    if previousDay and previousDay[23]["PrecipitationSummary"]["Past24Hours"]["Imperial"]["Value"] >= 0.15:
        #print(previousDay[23]["PrecipitationSummary"]["Past24Hours"]["Imperial"]["Value"])
        return True
    
    return False

"""Checks if it is currently raining, rained 3 hours ago, or rained 6 hours ago"""
def currentDayRain():

    currentDay = openJson('current_conditions.json')

    if currentDay[0]["HasPrecipitation"] == True:
        return True
    if currentDay[0]["PrecipitationSummary"]["Past3Hours"]["Imperial"]["Value"] > 0.0:
        return True
    if currentDay[0]["PrecipitationSummary"]["Past6Hours"]["Imperial"]["Value"] > 0.0:
        return True
        
    return False

"""Checks if there will be rain tomorrow and if it is above 70% chance and over 0.15 inches, then no irrigation"""
def willRainNextDay():
    nextDay = openJson('five_day_forcast.json')

    if(nextDay["DailyForecasts"][0]["Day"]["RainProbability"] >= 70) and (nextDay["DailyForecasts"][0]["Day"]["TotalLiquid"]["Value"] >= 0.15):
        return False

    return True

"""Will turn on the irrigation systems"""
def irrigate():

    relay.on()
    # imitate irrigation for a while
    sleep(5)
    # turn off irrigation
    relay.off()

#
#           END IRRIGATION LOGIC
#

# retrieve keys and json data from API
locationKey = postalCodeSearch(41001, API_KEY)

locationConditions = getCurrentConditions(locationKey, API_KEY)
if locationConditions:
    saveToJson(locationConditions, 'current_conditions')

lastDayConditions = getLastDayConditions(locationKey, API_KEY)
if lastDayConditions:
    saveToJson(lastDayConditions, 'last_day_conditions')
    
fiveDayForcast = getFiveDayForcast(locationKey, API_KEY)
if fiveDayForcast:
    saveToJson(fiveDayForcast, 'five_day_forcast')

# Main loop
while True:

    #checking Json data from API
    if previousDayHasSignificantRain() == True:
        LCD.lcd_clear()
        LCD.lcd_display_string("No Irrigation", 1)
        LCD.lcd_display_string("Rained Yesterday", 2)

    elif currentDayRain() == True:
        LCD.lcd_clear()
        LCD.lcd_display_string("No Irrigation", 1)
        LCD.lcd_display_string("Rained Today", 2)

    elif willRainNextDay() == True:
        LCD.lcd_clear()
        LCD.lcd_display_string("No Irrigation", 1)
        LCD.lcd_display_string("Rain Tomorrow", 2)

    else:
        LCD.lcd_clear()
        LCD.lcd_display_string("Starting", 1)
        LCD.lcd_display_string("    Irrigation", 2)
        irrigate()

    sleep(20)

