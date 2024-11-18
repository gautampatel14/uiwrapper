import urllib.error
import urllib.parse
import urllib.request
from collections import namedtuple
from typing import Optional

import requests

from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class ConfigManager:
    def __init__(self, username, password, url) -> None:
        self.params = {"count": 0, "output_mode": "json"}
        self.creds = (username, password)
        self.url = url

    def get_config(
        self, url, single_stanza: bool = False, filter: Optional[list] = None
    ):
        """
        Get the the stanza of the configuration of given filter.
            :params url: The endpoint URL for the configuration.
            :params single_stanza: If set True, return the first stanza of the filtered configuration.
            :params filter: Filter(stanza name) get specific configuration.
        """
        url = f"{url}?{urllib.parse.urlencode(self.params)}"
        res = requests.get(url, auth=self.creds, verify=False)
        LOGGER.debug(
            "method='GET', url={}, filter={} return with status_code={}, reason={}".format(
                url, filter, res.status_code, res.reason
            )
        )
        res = self.parse_configuration(res.json())
        if filter:
            res = self.filter(res, filter, single_stanza)
        return res

    def post_config(self, url, data: dict):
        """
        Create the configuration stanza by sending the provided data to the specified URL.
            :params url: The endpoint URL for the configuration.
            :params data: The configuration data to be sent in the request body.
        """

        data["output_mode"] = "json"
        res = requests.post(url, data, auth=self.creds, verify=False)
        LOGGER.debug(
            "method='POST', url={} return with status_code={}, reason={}".format(
                url, res.status_code, res.reason
            )
        )
        return res

    def update_config(self, url, data: dict):
        """
        Update the configuration by sending the provided data to the specified URL.
            :params url: The endpoint URL for the configuration.
            :params data: The configuration data to be sent in the request body to update the config.
        """
        data["output_mode"] = "json"
        res = requests.put(url, data, auth=self.creds, verify=False)
        LOGGER.debug(
            "method='POST', url={} return with status_code={}, reason={}".format(
                url, res.status_code, res.reason
            )
        )
        return res

    def delete_config(self, url, stanza: str):
        """
        Delete the stanza of the configuration.
            :params url: The endpoint URL for the configuration.
            :params stanza: The stanza of the configuration to delete. to delete stanza of multi-input configurations,
                specify the name along with the input type in the format "type_of_mod_input://input_name_to_delete"
        """
        url = "{}/{}".format(url, urllib.parse.quote_plus(stanza))
        res = requests.delete(url, auth=self.creds, verify=False)
        LOGGER.debug(
            "method='DELETE', url={}, stanza={} return with status_code={}, reason={}".format(
                url, stanza, res.status_code, res.reason
            )
        )
        return res

    def delete_all_config(self, url, filter: Optional[list] = None):
        """
        Delete the all stanza of the configuration of provided filtered.
            :params url: The endpoint URL for the configuration.
            :params filter: List of configuration stanza to delete.
        """
        responses = {"status_codes": [], "reasons": [], "texts": []}
        Response = namedtuple("Response", ["status_code", "reason", "text"])
        all_stanzas = list(self.get_config(url=url, filter=filter).keys())

        for stanza in all_stanzas:
            res = self.delete_config(url, stanza)
            responses["status_codes"].append(res.status_code)
            responses["reasons"].append(res.reason)
            responses["texts"].append(res.text)

        if all(code == 200 for code in responses["status_codes"]):
            return Response(status_code=200, reason="OK", text="Success")

        return Response(
            status_code=404,
            reason="Not Found",
            text="Failure",
        )

    def parse_configuration(self, response_data) -> dict:
        """
        Process the JSON response and construct a configuration dictionary.

            :param response_data: The JSON response obtained from the request.
            :param return_first: If True, only the first configuration stanza is returned.
            :return: A dictionary with configuration settings.
        """
        configuration = {}

        entries = response_data.get("entry")
        if not entries:
            return configuration

        for entry in entries:
            key = entry.get("name")
            if not key:
                continue

            content = entry.get("content", {})
            configuration[key] = {
                param: content[param]
                for param in content
                if not param.startswith("eai:")
            }
        return configuration

    def filter(
        self, response_data, keys_to_filter: list, single_stanza: bool = False
    ) -> dict:
        """
        Filters the response data based on a list of keys and optionally returns only the first stanza.
            :params response_data: The data to be filter.
            :params keys_to_filter: List of keys to be find from the data.
            :params first_stanza: If True, returns only the first stanza if multiple found. Defaults to False.
            :return: A Dictionary of filter urls.
        """
        filtered_urls = {
            key: value
            for key, value in response_data.items()
            if any(k in key for k in keys_to_filter)
        }
        if single_stanza:
            LOGGER.debug("Filter: {}".format(filtered_urls))
            return filtered_urls[next(iter(filtered_urls))]

        return filtered_urls
