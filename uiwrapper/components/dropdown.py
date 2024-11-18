from typing import Optional

from selenium.webdriver.common.by import By

from uiwrapper.actions.component_action import ComponentAction
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class DropDown(ComponentAction):
    """
    A class for interacting with dropdown elements on a web page using Selenium WebDriver.
    """

    INPUT_VALUES_LOCATOR = (
        ' [data-test="item"]:not([data-test-selected="true"]) [data-test="label"]'
    )
    LABEL = ' [data-test="label"]'
    POPOVER = ' [data-test="popover"]'

    def __init__(
        self,
        driver,
        name: str,
        value: str,
        by: Optional[str] = None,
        multi_input: bool = False,
    ):
        """
        Initializes the DropDown with the provided WebDriver, name, value, locator type, and multi-input flag.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the dropdown.
            :param value: The value used to locate the dropdown.
            :param by: The type of locator to use. Defaults to None.
            :param multi_input: Flag indicating if the dropdown allows multiple selections. Defaults to False.
        """
        self.is_multi_input = multi_input
        self.dropdown_btn = name + "_type"
        container = {name: [by, value]}
        super().__init__(driver, container)

        dropdown_locators = {
            self.dropdown_btn: [by, value],
            "values": [None, self.POPOVER + self.LABEL],
            "menu": [None, self.POPOVER + ' [data-test="menu"]'],
            "selected_value": [
                None,
                value + ' [data-test="select"] [data-test="label"]',
            ],
        }

        self.locator.update_locaters(dropdown_locators)

    def select(self, value: str):
        """
        Selects a value from the dropdown.

            :param value: The value to be selected from the dropdown.
            :return: True if the value was successfully selected.
            :raises ValueError: If the given value is not found in the dropdown options.
        """
        LOGGER.info("Selecting Dropdown value '{}' from the dropdown.".format(value))
        self.click_element(self.dropdown_btn)
        self.wait_for_element("menu")

        element = self.get_element(*self.locator.get_locator(self.dropdown_btn))
        PATH = "#" + element.get_attribute("data-test-popover-id") + self.LABEL

        for option in self.driver.find_elements(By.CSS_SELECTOR, PATH):
            if option.text.strip().lower() == value.lower():
                option.click()
                return True
        else:
            LOGGER.error("DropDown: Given value '{}' is not found.".format(value))
            raise ValueError("Given value '{}' is not found.".format(value))

    def get_dropdown_values(self):
        """
        Retrieves all values from the dropdown.

            :return: A list of text values from the dropdown options.
        """
        val = []
        self.click_element(self.dropdown_btn)
        self.wait_for_element("menu")

        element = self.get_element(*self.locator.get_locator(self.dropdown_btn))
        PATH = "#" + element.get_attribute("data-test-popover-id") + self.LABEL

        options = self.driver.find_elements(By.CSS_SELECTOR, PATH)
        for element in options:
            text = element.text.strip()
            # there is the case where dropdown have the hidden options as empty str.
            if text != "":
                val.append(text)
        return val

    def get_selected_value(self):
        element = self.get_element(*self.locator.get_locator("selected_value"))
        return element.text.strip()
