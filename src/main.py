from PyNUTClient import PyNUT
from influxdb_client import InfluxDBClient
from util.vars import get_env_variable

import logging
import sys
import json
import time


logger = logging.getLogger("main")


def decode_nut_ups_vars(ups_vars: dict) -> dict:
    """
    PyNUTClient's GetUPSVars() returns a dict of byte strings. This function converts a bytestring dict to
    appropriate Python types.

    Args:
        ups_vars (dict): Dictionary output from PyNUTClient.GetUPSVars()
    
    Returns:
        dict: Formatted dictionary with decoded keys and values
    """
    decoded_vars = {}
    for key_bytes, value_bytes in ups_vars.items():
        key_str = key_bytes.decode('utf-8')
        value_str = value_bytes.decode('utf-8')

        try:
            decoded_vars[key_str] = int(value_str)
        except ValueError:
            try:
                decoded_vars[key_str] = float(value_str)
            except ValueError:
                decoded_vars[key_str] = value_str
    logger.debug("Decoded NUT Data:\n" + json.dumps(decoded_vars, indent=4))

    return decoded_vars


def main(config: dict):
    while True:
        for i in range(len(config["NUT_HOSTS"])):
            try:
                nut = PyNUT.PyNUTClient(host=config["NUT_HOSTS"][i], port=config["NUT_PORT"], login=config["NUT_LOGIN"], password=config["NUT_PASSWORD"])
                pynut_data = nut.GetUPSVars(ups=config["NUT_UPS_NAMES"][i])
                logger.info("(%s:%s - %s) Got %s vars from NUT", config["NUT_HOSTS"][i], config["NUT_PORT"], config["NUT_UPS_NAMES"][i], len(pynut_data))
            except Exception as e:
                logger.error(e)
            decoded_pynut_data = decode_nut_ups_vars(pynut_data)

            tags = {
                "host": config["NUT_HOSTS"][i],
                "ups": config["NUT_UPS_NAMES"][i]
            }

            try:
                logger.info("(%s:%s - %s) Writing influx point data to %s", config["NUT_HOSTS"][i], config["NUT_PORT"], config["NUT_UPS_NAMES"][i], config["INFLUXDB2_HOST"], )
                with InfluxDBClient(url=config["INFLUXDB2_HOST"], token=config["INFLUXDB2_TOKEN"], org=config["INFLUXDB2_ORG"]) as client:
                    with client.write_api() as write_api:
                        write_api.write(config["INFLUXDB2_BUCKET"], config["INFLUXDB2_ORG"], [{
                            "measurement": "ups",
                            "tags": tags,
                            "fields": decoded_pynut_data
                        }])
            except Exception as e:
                logger.error(e)
        
        time.sleep(config["UPDATE_FREQUENCY"])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    logger.info("Logging started!")

    var_config = {
        "NUT_HOSTS": get_env_variable("NUT_HOSTS", list),
        "NUT_UPS_NAMES": get_env_variable("NUT_UPS_NAMES", list),
        "NUT_PORT": get_env_variable("NUT_PORT", int, required=False, default=3493),
        "NUT_LOGIN": get_env_variable("NUT_LOGIN", str),
        "NUT_PASSWORD": get_env_variable("NUT_PASSWORD", str),
        "INFLUXDB2_HOST": get_env_variable("INFLUXDB2_HOST", str),
        "INFLUXDB2_ORG": get_env_variable("INFLUXDB2_ORG", str),
        "INFLUXDB2_BUCKET": get_env_variable("INFLUXDB2_BUCKET", str),
        "INFLUXDB2_TOKEN": get_env_variable("INFLUXDB2_TOKEN", str),
        "UPDATE_FREQUENCY": get_env_variable("UPDATE_FREQUENCY", int, required=False, default=60)
    }

    config_print = var_config.copy()
    config_print["NUT_PASSWORD"] = "snip"
    config_print["INFLUXDB2_TOKEN"] = "snip"
    logger.info("Loaded Environment Configuration:\n%s", json.dumps(config_print, indent=4))

    main(var_config)
