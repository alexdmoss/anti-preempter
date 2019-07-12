import os
import logging
from dateutil import parser
from time import gmtime, strftime

logger = logging.getLogger(__name__)


def get_current_time_as_seconds():
    return strftime("%s", gmtime())


def get_time_as_seconds_since_epoch(ts) -> str:
    dt = parser.parse(ts)
    return dt.strftime("%s")


def get_env_variable(env_var: str) -> str:
    var_name = os.getenv(env_var)
    if var_name is None:
        raise EnvironmentError(env_var, " environment variable is not set")
    return var_name
