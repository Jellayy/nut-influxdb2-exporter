import os
import ast
import logging

from typing import Any


logger = logging.getLogger("vars")


def get_env_variable(var_name: str, var_type: Any, required: bool = True, default: Any = None, min_length: int = 1, allow_empty_string: bool = False) -> Any:
    """
    Retrieves string-based environment variables and casts them to defined types. Also adds provisions
    for required variables and default values. Supported types: str, bool, int, list

    Args:
        var_name (str): Name of the variable in the environment. Used to query variable from system env
        var_type (Any): Python type to attempt to cast var to
        required (bool, optional): Whether we should exit if the variable doesn't exist, defaults to True.
        default (Any, optional): If variable is not required, default value to return
        min_length (int, optional): If targeted type is list, minimum list length to accept. Defaults to 1.
        allow_empty_string (bool, optional): Whether strings should be allowed to be empty. Defaults to False.

    Returns:
        Any: The validated and converted variable value
    """
    value = os.getenv(var_name)

    if value is None:
        if required:
            logger.error("Required environment variable %s is not set", var_name)
            exit(1)
        return default
    
    if var_type is str:
        if not allow_empty_string and value == "":
            logger.error("Environment variable %s cannot be an empty string", var_name)
            exit(1)
        return value
    elif var_type is bool:
        if value.lower() in ("true", "1", "t", "y", "yes"):
            return True
        elif value.lower() in ("false", "1", "f", "n", "no"):
            return False
        else:
            logger.error("Environment variable %s must be a boolean string", var_name)
            logger.error("(e.g. 'true', 'false') Got: %s", value)
            exit(1)
    elif var_type is int:
        try:
            return int(value)
        except ValueError:
            logger.error("Environment variable %s must be an integer", var_name)
            logger.error("Got %s", value)
            exit(1)
    elif var_type is list:
        try:
            parsed_list = ast.literal_eval(value)
            if not isinstance(parsed_list, list):
                logger.error("Environment variable %s is not in a valid list format", var_name)
                exit(1)
            if len(parsed_list) < min_length:
                logger.error("Environment variable %s must contain at least %s entries", var_name, min_length)
                logger.error("Got %s entries", len(parsed_list))
                exit(1)
            return parsed_list
        except (SyntaxError, ValueError) as e:
            logger.error("Environment variable %s must be a valid list string", var_name)
            logger.error("(e.g. \"['item1', 'item2']\") Got %s", value)
            exit(1)
    else:
        logger.critical("Attempeted to load unimplemented var type: %s", var_type)
        logger.critical("This should not happen and is not user error.")
        exit(1)
        