# NUT-InfluxDB2-Exporter (WIP)

Semi-inspired by [kiwimato/nut-influxdb-exporter](https://github.com/kiwimato/nut-influxdb-exporter) & [dbsqp/nut-influxdb2](https://github.com/dbsqp/nut-influxdbv2). Both have been abandoned in favor of Telegraf and weren't configurable enough to fit my setup.

Simple script/container for polling data from one or more NUT servers and pushing to an InfluxDB2 bucket.

> [!CAUTION]
> NUT & the PyNUTClient library use telnet for communications under the hood. With the nature of what NUT is used for this should already be implied, but DO NOT deploy this over anything but a very private network.

# Deployment

### Docker Compose
```yml
services:
    nut-influxdb2-exporter:
        image: jellayy/nut-influxdb2-exporter:latest
        environment:
            NUT_HOSTS: "['192.168.1.2', '...']"
            NUT_UPS_NAMES: "['rack-ups', '...']"
            NUT_PORT: 3493 # optional
            NUT_LOGIN: nut_user
            NUT_PASSWORD: nut_pass
            INFLUXDB2_HOST: https://influx.local:1234
            INFLUXDB2_ORG: org_name
            INFLUXDB2_BUCKET: bucket_name
            INFLUXDB2_TOKEN: token
            UPDATE_FREQUENCY: 60 # seconds, optional
        restart: unless-stopped
```

### Docker CLI
```bash
docker run -d \
    --name nut-influxdb2-exporter \
    -e NUT_HOSTS="['192.168.1.2', '...']" \
    -e NUT_UPS_NAMES="['rack-ups', '...']" \
    -e NUT_PORT=3493 \
    -e NUT_LOGIN=nut_user
    -e NUT_PASSWORD=nut_pass \
    -e INFLUXDB2_HOST=https://influx.local:1234 \
    -e INFLUXDB2_ORG=org_name \
    -e INFLUXDB2_BUCKET=bucket_name \
    -e INFLUXDB2_TOKEN=token \
    -e UPDATE_FREQUENCY=60 \
    --restart unless-stopped \
    jellayy/nut-influxdb2-exporter:latest
```

> [!NOTE]
> This script is designed to error and continue and will not stop if NUT or Influx calls aren't working. If data isn't showing up where expected, check the logs