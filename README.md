# NUT-InfluxDB2-Exporter (WIP)

> [!CAUTION]
> NUT & the PyNUTClient library use telnet for communications under the hood. With the nature of what NUT is used for this should already be implied, but DO NOT deploy this over anything but a very private network.

> [!INFO]
> This script is designed to error and continue and will not stop if NUT or Influx calls aren't working. If data isn't showing up where expected, check the logs