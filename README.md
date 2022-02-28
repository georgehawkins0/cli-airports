# cli-airports
 
A command line based application for gathering information on a specific airport using a flightradar24 api.

Here are some usage examples:

1. Fetch **arrivals** to **LHR** (London Heathrow):

        $ airports.py --mode arrivals --airport LHR

2. Fetch **15 departures** from **DXB**, 

        $ airports.py --mode departures --airport DXB --limit 15

    And with export:

        $ airports.py --mode departures --airport DXB --limit 15 --export

3. Fetch general airport information for **CDG**

        $ airports.py --mode info --airport CDG

4. Find IATA code for  **London Stansted**

        $ airports.py --name "London Stansted"


      *Note, " is required either side for a search with more than one word.*

### Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [To-do](#To-do)

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
usage: airports.py [-h] [-m MODE] [-a AIRPORT] [-l LIMIT] [-n NAME] [-e]

Information about any airport from all over the world.

options:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  Mode (arrivals/departures/weather/info)
  -a AIRPORT, --airport AIRPORT
                        The IATA airport code
  -l LIMIT, --limit LIMIT
                        Limit to show (default 10, max for all)
  -n NAME, --name NAME  Search for an airport name. Returns airports with a matching name. Useful for finding IATA
                        code.
  -e, --export          save results in a JSON file

```

## To-do

- ~~airport name search for IATA code~~ Done v1.1
- Live flight tracker