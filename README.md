# MobilityIndexRetriever
Retrieve the intercity, intracity mibility data

### Requirements

Please install `click`, `requests`, `pandas`, `china_cities`, `pypinyin` with `pip` before using the script.

### Usage

The script `retrieve_mobility_index` is in the scripts directory.

```shell
Usage: retrieve_mobility_index.py [OPTIONS]

  Retrieve the mobility data from Baidu Huiyan

      Arguments:

          app {str} -- The application to call: `intercity` (flows from a
          given city to top 100 cities or flows to  a given city from top
          100 cities for given date range), `intracity` (within a city) or
          `history` (all flow from or to a given city in history).

          city {str} -- The city where the flows to or from, in the format
          of "Province City" e.g. "Hubei Wuhan"

          move {str} -- move in (to) or out (from)

          date {str} -- date or date range (only for intercity), e.g.
          "2020-03-01" or "2020-03-01:2020-03-07"

          output {str} -- The output file name



Options:
  -a, --app [intercity|intracity|history]
  --city TEXT                     The "province city" for which to extract
                                  data (must be quoted: e.g. "Hubei Wuhan")
  -m, --move [in|out]             Data for move in, out of the city (for
                                  intercity and history)
  -d, --date TEXT                 Date in format of "2020-03-01" or range
                                  "2020-03-01:2020-03-26" for intercity
  -o, --output TEXT               The output file name
  --help                          Show this message and exit.
```