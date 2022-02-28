import requests
import json
from datetime import datetime
import argparse
import sys
import json
import time

def stampToDate(timestamp):
    if timestamp:
        dtObject = datetime.fromtimestamp(timestamp)
        return str(dtObject)
    else:
        return "NA"

def noneConverter(callsign):
    if callsign:
        return callsign
    else:
        return "None"

def statusConverter(status):
    if status == False:
        return "Not departed"
    else:
        return "Departed"

def apiReq(airport,arrivalsOrDepartures,page):
    _headers = {
        'authority': 'api.flightradar24.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'accept': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'user-agent': '',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://www.flightradar24.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.flightradar24.com/',
        'accept-language': '',
    }

    _params = (
        ('code', airport),
        ('plugin/[/]', 'schedule'),
        ('plugin-setting/[schedule/]/[mode/]', arrivalsOrDepartures),
        ('plugin-setting/[schedule/]/[timestamp/]', '0'),
        ('page', page),
        ('limit', '100'),
        ('token', ''),
    )
    r = requests.get('https://api.flightradar24.com/common/v1/airport.json', params=_params,headers=_headers)

    response = json.loads(r.text) #dict_keys(['result', '_api'])
    return response

def getFlightData(airport,arrivalsOrDepartures,limit): # uses apiReq, this function gets every page instead of just the first one (which is default by apiReq)
    data = {"name":None,"data":[]}
    response = apiReq(airport,arrivalsOrDepartures,1)

    if "result" not in response: # if the api says invalid code (when the codes are longer than 4 chars)
        raise ValueError("Incorrect IATA airport code")
    if "details" not in response["result"]["response"]["airport"]["pluginData"]: # if result is obviously not an airport (returns this when its a 4 or less length code)
            raise ValueError("Incorrect IATA airport code")
            # just for information: The api essentially thinks that any 4 or fewer digit code is a valid airport, it just doesnt respond with any information.

    data["name"] = response["result"]["response"]["airport"]["pluginData"]["details"]["name"]

    pages = response["result"]["response"]["airport"]["pluginData"]["schedule"][arrivalsOrDepartures]["page"]["total"] # total amount of pages of information that the api can provide
    for i in range(pages):
        response = apiReq(airport,arrivalsOrDepartures,i+1) # page starts at 1
        responseData = response["result"]["response"]["airport"]["pluginData"]["schedule"][arrivalsOrDepartures]["data"]
        for flight in responseData: 
            if "destination" in flight["flight"]["airport"]:
                if "name" not in flight["flight"]["airport"]["destination"]:
                    flight["flight"]["airport"]["destination"]["name"] = None
            if "origin" in flight["flight"]["airport"]:
                if "name" not in flight["flight"]["airport"]["origin"]:
                    flight["flight"]["airport"]["origin"]["name"] = None
            # ^ because i'm fairly certian for some flights (quite rare) the origin/destination is unknown (origin for arrivals, destination for departures)
        data["data"]+=responseData
        if len(data["data"]) >= limit:
            break
    return data


def getArrivals(airport,limit,export=False):
    if limit == "max":
        limit = 99999 # this is bad code but its new years day and im tired
    limit = int(limit)

    print ("Fetching", end="\r")
    data = getFlightData(airport,"arrivals",limit)
    flightData = data["data"]
    airportName = data["name"]
    if len(data) == 0:
        return "No arrivals to show" # OR something else wrong with API

    longestCallsign = max([max(len(noneConverter(flight["flight"]["identification"]["number"]["default"])) for flight in flightData),6])
    longestOrigin = max([max(len(noneConverter(flight["flight"]["airport"]["origin"]["name"])) for flight in flightData),6])
    longestScheduledArrival = max([max(len(stampToDate(flight["flight"]["time"]["scheduled"]["arrival"])) for flight in flightData),17])
    longestEstimatedArrival = max([max(len(stampToDate(flight["flight"]["time"]["estimated"]["arrival"])) for flight in flightData),17])
    longestStatus =  max([max(len(statusConverter(flight["flight"]["status"]["live"])) for flight in flightData),6])

    callsignSpace = longestCallsign + 3
    originSpace = longestOrigin + 3
    scheduledArrivalSpace = longestScheduledArrival + 3
    estimatedArrivalSpace = longestEstimatedArrival + 3
    longestStatusSpace = longestStatus + 3

    if limit == "max":
        limit = len(flightData)
    limit = int(limit)
    if limit > len(flightData):
        limit = len(flightData)

    print(f"Arrivals at {airportName}")
    print(f"Displaying {limit} of {len(flightData)} arrivals \n\n")
    print("Flight {}Origin {}Scheduled Arrival {}Estimated Arrival{} Status\n".format(" "*(callsignSpace-6)," "*(originSpace-6)," "*(scheduledArrivalSpace-17)," "*(estimatedArrivalSpace-17)))
    for flight in flightData[0:limit]:
        flight = flight["flight"]
        callsign = flight["identification"]["number"]["default"]
        origin = flight["airport"]["origin"]["name"]
        scheduledArrival = flight["time"]["scheduled"]["arrival"]
        estimatedArrival =  flight["time"]["estimated"]["arrival"]
        status = flight["status"]["live"]
        print(callsign," "*(callsignSpace-(len(noneConverter(callsign)))),end="")
        print(origin," "*(originSpace-(len(noneConverter(origin)))),end="")
        print(stampToDate(scheduledArrival)," "*(scheduledArrivalSpace-(len(stampToDate(scheduledArrival)))),end="")
        print(stampToDate(estimatedArrival)," "*(estimatedArrivalSpace-(len(stampToDate(estimatedArrival)))),end="")
        print(statusConverter(status)," "*(longestStatusSpace-8))

    if export:
        exportData = {"arrivals":[]}
        for flight in flightData:
            d = {}
            flight = flight["flight"]
            d["callsign"] = flight["identification"]["number"]["default"]
            d["origin"] = flight["airport"]["origin"]["name"]
            d["scheduledArrival"] = flight["time"]["scheduled"]["arrival"]
            d["estimatedArrival"] =  flight["time"]["estimated"]["arrival"]
            d["status"] = flight["status"]["live"]
            exportData["arrivals"].append(d)

        current_time = int(time.time())
        filename = f"{airport}_arrivals_{current_time}"

        with open(f'out\{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(exportData, f, ensure_ascii=False, indent=4)

        print(f"Sucessfully exported arrival data to {filename}")


def getDepartures(airport,limit,export=False):
    if limit == "max":
        limit = 99999 # this is bad code but its new years day and im tired
    limit = int(limit)

    print ("Fetching", end="\r")
    data = getFlightData(airport,"departures",limit)
    flightData = data["data"]
    airportName = data["name"]
    if len(data) == 0:
        return "No departures to show" # OR something else wrong with API

    longestCallsign = max([max(len(noneConverter(flight["flight"]["identification"]["number"]["default"])) for flight in flightData),6]) # the second max is for the header of the column
    longestDestination = max([max(len(noneConverter(flight["flight"]["airport"]["destination"]["name"])) for flight in flightData),11])
    longestScheduledDeparture = max([max(len(stampToDate(flight["flight"]["time"]["scheduled"]["departure"])) for flight in flightData),17])
    longestEstimatedDeparture = max([max(len(stampToDate(flight["flight"]["time"]["estimated"]["departure"])) for flight in flightData),17])
    longestStatus =  max([max(len(statusConverter(flight["flight"]["status"]["live"])) for flight in flightData),6])

    callsignSpace = longestCallsign + 3 # 3 is our chosen smallest space
    destinationSpace = longestDestination + 3
    scheduledDestinationSpace = longestScheduledDeparture + 3
    estimatedDestinationSpace = longestEstimatedDeparture + 3
    longestStatusSpace = longestStatus + 3

    if limit == "max":
        limit = len(flightData)
    limit = int(limit)
    if limit > len(flightData):
        limit = len(flightData)

    print(f"Departures at {airportName}")
    print(f"Displaying {limit} of {len(flightData)} departures \n\n")
    print("Flight {}Destination {}Scheduled Departure {}Estimated Departure {}Status\n".format(" "*(callsignSpace-6)," "*(destinationSpace-11)," "*(scheduledDestinationSpace-19)," "*(estimatedDestinationSpace-19)))
    for flight in flightData[0:limit]:
        flight = flight["flight"]
        callsign = flight["identification"]["number"]["default"]
        destination = flight["airport"]["destination"]["name"]
        scheduledDeparture = flight["time"]["scheduled"]["arrival"]
        estimatedDeparture =  flight["time"]["estimated"]["arrival"]
        status = flight["status"]["live"]
        print(callsign," "*(callsignSpace-(len(noneConverter(callsign)))),end="")
        print(destination," "*(destinationSpace-(len(noneConverter(destination)))),end="")
        print(stampToDate(scheduledDeparture)," "*(scheduledDestinationSpace-(len(stampToDate(scheduledDeparture)))),end="")
        print(stampToDate(estimatedDeparture)," "*(estimatedDestinationSpace-(len(stampToDate(estimatedDeparture)))),end="")
        print(statusConverter(status)," "*(longestStatusSpace-8))

    if export:
        exportData = {"departures":[]}
        for flight in flightData:
            d = {}
            flight = flight["flight"]
            d["callsign"] = flight["identification"]["number"]["default"]
            d["destination"] = flight["airport"]["destination"]["name"]
            d["scheduledDeparture"] = flight["time"]["scheduled"]["arrival"]
            d["estimatedDeparture"] =  flight["time"]["estimated"]["arrival"]
            d["status"] = flight["status"]["live"]
            exportData["departures"].append(d)

        current_time = int(time.time())
        filename = f"{airport}_departures_{current_time}"

        with open(f'out\{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(exportData, f, ensure_ascii=False, indent=4)

        print(f"Sucessfully exported departure data to {filename}.json")
    
def generalAirportInfo(airport):
    response = apiReq(airport,"arrivals",1)

    if "result" not in response: # if the api says invalid code
        raise ValueError("Incorrect IATA airport code")
    if "details" not in response["result"]["response"]["airport"]["pluginData"]: # if result is obviously not an airport
            raise ValueError("Incorrect IATA airport code")

    name = response["result"]["response"]["airport"]["pluginData"]["details"]["name"]
    timezoneName = response["result"]["response"]["airport"]["pluginData"]["details"]["timezone"]["abbrName"]
    timezoneOffset = response["result"]["response"]["airport"]["pluginData"]["details"]["timezone"]["offset"]/(60*60)
    totalAirplanes = response["result"]["response"]["airport"]["pluginData"]["aircraftCount"]["ground"]
    runways = response["result"]["response"]["airport"]["pluginData"]["runways"]

    print(f"General information about {name}\n")
    print(f"Timezone: {timezoneName} (offset: {timezoneOffset}h)")
    print(f"Total airplanes on ground: {totalAirplanes}")
    print(f"Total runways: {len(runways)}\nList of runways:")
    for runway in runways:
        print(" Name: {}, Length: {}m".format(runway["name"],runway["length"]["m"]))

def getWeather(airportCode):
    print ("Fetching", end="\r")
    response = apiReq(airportCode,"departures",1)

    if "result" not in response: # if the api says invalid code
        raise ValueError("Incorrect IATA airport code")
    if "details" not in response["result"]["response"]["airport"]["pluginData"]: # if result is obviously not an airport
            raise ValueError("Incorrect IATA airport code")

    data = response["result"]["response"]["airport"]["pluginData"]["weather"]
    airportName = response["result"]["response"]["airport"]["pluginData"]["details"]["name"]
    
    weatherData = {}
    weatherData["Temperature (c)"] = data["temp"]["celsius"]
    weatherData["Sky Condition"] = data["sky"]["condition"]["text"]
    weatherData["Wind speed (kts)"] = data["wind"]["speed"]["kts"]
    weatherData["Wind speed comment"] = data["wind"]["speed"]["text"]
    weatherData["Wind direction"] = "{} ({})".format(data["wind"]["direction"]["degree"],data["wind"]["direction"]["text"])
    weatherData["Visibility (mi)"] = data["sky"]["visibility"]["mi"]
    weatherData["Pressure (hPa)"] = data["pressure"]["hpa"]
    weatherData["Dew point (celcius)"] = data["dewpoint"]["celsius"]
    weatherData["Humidity"] = data["humidity"]
    # weatherData["Elevation (m)"] = data["elevation"]["m"] # > not really weather info but more than welcome to uncomment the line if you want this
    
    print("Here are the current weather conditions at {}\n".format(airportName))
    for stat in weatherData:
        print(f"{stat}: {weatherData[stat]}")

def getResults(name):
    headers = {
        'authority': 'www.flightradar24.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '',
        'sec-ch-ua-mobile': '?0',
        'user-agent': '',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.flightradar24.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': ''
        }

    params = (
        ('query', name),
        ('limit', '50'),
    )

    response = requests.get('https://www.flightradar24.com/v1/search/web/find', headers=headers, params=params)

    result = response.json()

    return result

parser = argparse.ArgumentParser(description="Information about any airport from all over the world.")

parser.add_argument('-m', '--mode', type=str, default=None, help="Mode (arrivals/departures/weather/info)")
parser.add_argument('-a', '--airport', type=str, default=None, help="The IATA airport code")
parser.add_argument('-l', '--limit', type=str, default="10", help="Limit to show (default 10, max for all)")
parser.add_argument('-n', '--name', type=str, default=None, help="Search for an airport name. Returns airports with a matching name. Useful for finding IATA code.")
parser.add_argument('-e', '--export', help='save results in a JSON file', action='store_true')


if __name__ == "__main__":
    helpMessage = """Flights.py\nInformation about airports all over the world.
    Arguments: 
    --mode

        arrivals: finds all the available arrivals to a given airport. To specify how many results to show, use the --limit argument.
        departures: finds all the available departures from a given airport. To specify how many results to show, use the --limit argument.
        weather: shows the current weather at a given airport.
        info: gives general airport information.


    --airport

        A valid IATA airport code.


    --name Search for an airport name. Returns airports with a matching name. Useful for finding IATA code


    --limit

        How many results to show on the page.


    --export

        For saving results in a JSON file.
    
    
    """

    args = parser.parse_args()
    if len(sys.argv) > 1:
        if args.mode in ["arrivals","arrival"]:
            if args.airport and args.limit.isdigit() == True or args.limit.lower() == "max":
                getArrivals(args.airport,args.limit,args.export)
            elif args.limit.lower() != "max" and args.airport:
                print("Invalid limit")
            else:
                raise SyntaxError("No airport IATA code given")

        elif args.mode in ["departures","departure"]:
            if args.airport and args.limit.isdigit() == True or args.limit.lower() == "max":
                getDepartures(args.airport,args.limit,args.export)
            elif args.limit.lower() != "max" and args.airport:
                print("Invalid limit")
            else:
                raise SyntaxError("No airport IATA code given")
        
        elif args.mode in ["weather","weathers"]:
            if args.airport:
                getWeather(args.airport)
            else:
                raise SyntaxError("No airport IATA code given")

        elif args.mode in ["info","information","informations","infos","general"]:
            if args.airport:
                generalAirportInfo(args.airport)
            else:
                raise SyntaxError("No airport IATA code given")

        elif args.name:
            result = getResults(args.name)
            if len(result["results"]) !=0:
                print(f"Displaying search results for search query {args.name}")
                for item in result["results"]:
                    print(item["label"])
            else:
                print("No results found.")
                
        else:
            raise ValueError(f"Invalid mode \"{args.mode}\"")
    else:
        print(helpMessage)