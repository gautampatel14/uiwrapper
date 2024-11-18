from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertSelect(AlertBaseComponent):
    def __init__(
        self,
        driver,
        name: str,
        value: str,
        by: Optional[str] = None,
    ):
        """
        Initializes the AlertSelect with the provided WebDriver, name, value, locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the AlertSelect.
            :param value: The value used to locate the AlertSelect.
            :param by: The type of locator to use. Defaults to None.
        """
        LOGGER.info("Adding AlertSelect.... {}".format(name))
        self.name = name
        container = {name: [by, value]}
        super().__init__(driver, container)
        self.locator.update_locaters(
            {
                name: [None, value + ' [data-test="select"]'],
                "menu": [None, '[data-test="menu"]'],
                "values": [None, '[data-test="option"]'],
            }
        )

    def select(self, value):
        """
        Select the value from the select options.
            :params value: The value to be selected.
        """
        LOGGER.info("Selecting: {}".format(value))
        self.wait_for_element(self.name)
        try:
            self.click_element(self.name)
        except:
            by, value = self.locator.get_locator(self.name)
            value = value + '[label="Select..."]'
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            element.click()

        self.wait_for_element("menu")
        for option in self._find_elements(*self.locator.get_locator("values")):
            LOGGER.info("option text: {}".format(option.text))
            if option.text.strip().lower() == value.lower():
                option.click()
                return True
        else:
            raise ValueError("Given value={} is not found.".format(value))

    def get_all_options(self) -> list:
        """
        Retrieves all options from the dropdown.

            :return: A list of all options in the dropdown.
        """
        self.wait_for_element(self.name)
        self.click_element(self.name)
        val = [
            element.text.strip()
            for element in self._find_elements(*self.locator.get_locator("values"))
        ]

        LOGGER.info("All options: {}".format(val))
        return val

    def selected_value(self) -> list:
        """
        Return the selected value.
            :returns List: return selected value list.
        """
        element = self.get_element(*self.locator.get_locator(self.name))
        return [element.get_attribute("data-test-value")]
