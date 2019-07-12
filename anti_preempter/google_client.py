import logging
import json
import sys
from anti_preempter.utils import get_env_variable
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
from google.oauth2 import service_account

# suppresses noisy warning for cache_discovery when using oauth>4.0
# plus unnecessary INFO level URL requests
logging.getLogger("googleapiclient").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


def build_creds_object(var_name: str):
    creds_json = get_env_variable(var_name)
    sa_info = json.loads(creds_json)
    return service_account.Credentials.from_service_account_info(sa_info)


def google_api_create_service(api: str, version: str = "v1"):
    creds = build_creds_object('GOOGLE_CREDS')
    return build(*[api, version], **{'credentials': creds})


def google_api_call(request: HttpRequest):
    try:
        return request.execute()
    except Exception:
        logger.error('Call to Google Cloud Resource Manager API Failed!', sys.exc_info()[0])
