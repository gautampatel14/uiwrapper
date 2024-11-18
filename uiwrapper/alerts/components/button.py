from typing import Optional

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertButton(AlertBaseComponent):
    def __init__(self, driver, name: str, value: str, by: Optional[str] = None) -> None:
        """
        Initializes the Button class with the given WebDriver, locator name, type, and value.

            :param driver: WebDriver instance to interact with the web page.
            :param name: The name/key for the locator.
            :param by: The type of locator (e.g., By.ID, By.CSS_SELECTOR). Defaults to By.CSS_SELECTOR if not provided.
            :param value: The value of the locator. Defaults to None.
        """
        LOGGER.info("Adding button: {}".format(name))
        container = {name: [by, value]}
        super().__init__(driver, container)
        self.name = name

    def click(self):
        """
        Clicks the button element identified by its locator.
        Logs the locator information before clicking.
        """
        LOGGER.info("Clicking button with locator '{}'".format(self.name))
        self.click_element(self.name)

    def hover(self):
        """
        Hovers over the button element identified by its locator.

            :param locator: The name/key of the locator.
        """
        LOGGER.info("Hovering over button with locator '{}'".format(self.name))
        self._hover_element(self.name)
