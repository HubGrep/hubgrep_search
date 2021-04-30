"""
A CachedResponse is a wrapper for requests.Response, for serialization and caching.
"""

import json
import requests

from requests.exceptions import Timeout, ConnectionError, TooManyRedirects
from hubgrep.constants import UNKNOWN_ERROR, CONNECTION_ERROR, TIMEOUT_ERROR, TOO_MANY_REDIRECTS_ERROR

class CachedResponse:
    """
    Wrapper class for cached responses.

    url -
        url this request was made to
    success -
        True, if status_code was 2XX
    status_code -
        http status code of the response.
        will be `-1` if an exception was thrown, and we didnt get a status code.
    response_json -
        dict from the response json data
    error_msg -
        http error message, if we had a response code,
        otherwise the exception text
    """
    def __init__(self, url, success, status_code, response_json, error_msg):
        self.url = url
        self.success = success
        self.status_code = status_code
        self.response_json = response_json
        self.error_msg = error_msg

    def serialize(self) -> str:
        """ Serialize this CachedResponse. """
        d = dict(
            url=self.url,
            success=self.success,
            status_code=self.status_code,
            response_json=self.response_json,
            error_msg=self.error_msg,
        )
        return json.dumps(d)

    @staticmethod
    def from_serialized(data: str) -> "CachedResponse":
        """ Create a CachedResponse object from serialized CachedResponse. """
        d = json.loads(data)

        url = d["url"]
        success = d["success"]
        status_code = d["status_code"]
        response_json = d["response_json"]
        error_msg = d["error_msg"]
        result = CachedResponse(
            url=url,
            success=success,
            status_code=status_code,
            response_json=response_json,
            error_msg=error_msg,
        )
        return result

    @staticmethod
    def from_response(response: requests.Response) -> "CachedResponse":
        """ Create a CachedResponse object from a request.Response. """
        url = response.url
        status_code = response.status_code
        response_json = response.json()
        if response.ok:
            success = True
            error_msg = None
        else:
            success = False
            error_msg = response.text

        result = CachedResponse(
            url=url,
            success=success,
            status_code=status_code,
            response_json=response_json,
            error_msg=error_msg,
        )
        return result 

    @staticmethod
    def from_exception(url, exception) -> "CachedResponse":
        """ Create a CachedResponse object from an exception message. """
        if type(exception) is Timeout:
            status_code = TIMEOUT_ERROR
        elif type(exception) is ConnectionError:
            status_code = CONNECTION_ERROR
        elif type(exception) is TooManyRedirects:
            status_code = TOO_MANY_REDIRECTS_ERROR
        else:
            status_code = UNKNOWN_ERROR


        return CachedResponse(
            url=url,
            success=False,
            status_code=status_code,
            response_json=None,
            error_msg=str(exception),
        )

