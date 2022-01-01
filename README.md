# cli-airports
 
A command line based application for gathering information on a specific airport using a flightradar24 api.

Here are some usage examples:

1. Find **arrivals** to **LHR** (London Heathrow):

        $ flights.py --mode arrivals --airport LHR

2. Fetch **15 departures** from **DXB**, 

        $ flights.py --mode departures --airport DXB --limit 15

    And with export:

        $ flights.py --mode departures --airport DXB --limit 15 --export

3. Find general airport information for **CDG**

        $ flights.py --mode info --airport CDG

### Table of contents

- [Installation](#installation)
- [Usage](#usage)

### Installation


Clone the github repo
```
$ git clone https://github.com/georgehawkins0/cli-airports.git
```
Change Directory

```
$ cd cli-airports
```


### Usage
#### Cmdline options
```
usage: airports.py [-h] -m MODE -a AIRPORT [-l LIMIT] [-e]

Information about any airport from all over the world.

options:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  Mode (arrivals/departures/weather/info)
  -a AIRPORT, --airport AIRPORT
                        The IATA airport code
  -l LIMIT, --limit LIMIT
                        Limit to show (default 10, max for all)
  -e, --export          save results in a JSON file
```

## To-do

- airport name search for IATA code
- Live flight tracker