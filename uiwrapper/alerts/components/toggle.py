from typing import Optional

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertToggle(AlertBaseComponent):
    def __init__(self, driver, name: str, value: str, by: Optional[str] = None) -> None:
        """
        Initializes the AlertToggle with the provided WebDriver, name, value, locator type

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the Toggle(radio button).
            :param value: The value used to locate the Toggle(radio button).
            :param by: The type of locator to use. Defaults to None.
        """
        LOGGER.info("Adding Alert toggle: {}".format(name))
        container = {name: [by, value]}
        super().__init__(driver, container)
        self.name = name
        self.locator.update_locaters({"selected_value": [None, value + " .active"]})

    def select(self, value):
        """
        Select the toggle value.
            :param value: The value to be selected.
        """
        self.wait_for_element(self.name)
        for option in self._find_elements(*self.locator.get_locator(self.name)):
            if option.text.strip().lower() == value.lower():
                option.click()
                return True
        else:
            raise ValueError("Given value={} is not found.".format(value))

    def get_value(self):
        """
        Get the value of the toggle button (radio button).
        """
        self.wait_for_element(self.name)
        return self.get_text("selected_value")
