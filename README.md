# apic-latency-analytics

Tool for extracting latency data from API Connect analytics exports.

## Background

[API Connect](https://www.ibm.com/cloud/api-connect) offers a method to export analytics data in CSV format for analysis. The latency information supplied in this analytics data can be difficult to read or gain insight from without first manipulating or extracting the data. The purpose of this tool is to make the extraction of latency data from API Connect analytics much easier, so that you can spend more time troubleshooting or yielding insights from the data, and less time trying to work with the larger analytics CSV itself.

## Installation

This tool is currently only hosted on GitHub, it is not published to [PyPi](https://pypi.org/). This may be looked into in the future. For now, you can clone this repository or download the `apic-latency-analytics.py` script to run the tool.

## Running the script

The script must be run on at least one analytics CSV file. By default, if not extra arguments are provided, the script will output data in the format:

```
$ ./apic-lat.py test/min-latency-info2.csv
Loading file: test/min-latency-info2.csv
120,2019-06-26T06:16:35.587Z,1182337,test_api_name,Start=35,task1=69,task2=100,task3=106,task4=111,task5=115,task6=120
```

To break this down a bit, the data line there consists of the following data points:

- `time_to_serve_request`
- `@timestamp`
- `transaction_id`
- `api_name`
- Parsed `latency_info2` data

For specific details on the exposed API event record fields exported in the analytics CSV, please see API Connect's documentation [here](https://www.ibm.com/support/knowledgecenter/SSMNED_2018/com.ibm.apic.apionprem.doc/rapim_analytics_apieventrecordfields.html).

The script defaults to parsing `latency_info2`. You can switch to using `latency_info` by issuing the `--lat-info` command line argument when invoking the script. Per API Connect's documentation, the `latency_info2` field is only included in the user interface exported information.

The `time_to_serve_request` column is moved to the front, such that the output of this tool can easily be sorted by overall time to serve the API response, which usually is an easy way to isolate transactions with high latency.
