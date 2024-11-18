from typing import Optional

from selenium.webdriver.common.by import By

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class SearchQueryBox(AlertBaseComponent):
    def __init__(
        self,
        driver,
        name: str,
        value: str,
        by: Optional[str] = None,
    ):
        """
        Initializes the SearchQueryBox with the provided WebDriver, name, value, locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the SearchQueryBox.
            :param value: The value used to locate the SearchQueryBox.
            :param by: The type of locator to use. Defaults to None.
        """
        LOGGER.info("Adding SearchQueryBox: {}".format(name))
        self.name = name
        search_query_container = {name: [by, value]}
        super().__init__(driver, search_query_container)
        self.locator.update_locaters(
            {
                "text_container": [by, value + " .ace_editor"],
                name: [by, value + " .ace_content"],  # content selector.
            }
        )

    def set_value(self, value):
        """
        Set the searchquery value in SearchQuery box.
            :params value: The SearchQuery to search.
        """
        self.click_element("text_container")
        self.action.send_keys(value)
        self.action.perform()

    def get_value(self):
        """
        Get the SearchQuery box value.
            :returns str: return the search query.
        """
        self.wait_for_element(self.name)
        return self.get_element_text(*self.locator.get_locator((self.name)))
