from typing import Optional

from uiwrapper.components.base import Base
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class CheckBox(Base):
    """
    A class for interacting with checkbox elements on a web page using Selenium WebDriver.
    """

    CHECKBOX_BUTTON = ' [data-test="controls"] [data-test="button"][role="checkbox"]'
    CHECK_BOX = ' [data-test="controls"] [data-test="switch"]'
    CHECK_BOX_CONTROL_GROUP = '[data-test="control-group"][data-name="{}"]'

    def __init__(self, driver, name: str, value: str, by: Optional[str] = None):
        """
        Initializes the CheckBox with the provided WebDriver, name, value, and locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the checkbox.
            :param value: The value used to locate the checkbox.
            :param by: The type of locator to use. Defaults to None.
        """
        self.name = name
        self.checkbox = self.name + "_checkbox"
        self.checkbox_btn = self.name + "_checkbox_btn"
        self.value = self.CHECK_BOX_CONTROL_GROUP.format(value)
        container = {self.name: [by, self.value]}
        super().__init__(driver, container)

        checkbox_locator = {
            self.checkbox_btn: [by, self.value + self.CHECKBOX_BUTTON],
            self.checkbox: [by, self.value + self.CHECK_BOX],
        }
        self.locator.update_locaters(checkbox_locator)

    def check(self):
        """
        Checks the checkbox if it is not already checked.

            :return: True if the checkbox was checked, False if it was already checked.
            :raises Exception: If an error occurs while checking the checkbox.
        """
        LOGGER.info("Checking the checkbox.")
        try:
            self.wait_for_element(self.checkbox_btn)
            if not self.is_checked():
                LOGGER.info("Checkbox is not checked, clicking to check.")
                self.click_element(self.checkbox_btn)
                return True
            else:
                LOGGER.info("Checkbox is already checked.")
                return False
        except Exception as e:
            LOGGER.error("Failed to check checkbox with error: {}".format(e))
            raise

    def uncheck(self):
        """
        Unchecks the checkbox if it is currently checked.

            :return: True if the checkbox was unchecked, False if it was already unchecked.
            :raises Exception: If an error occurs while unchecking the checkbox.
        """
        LOGGER.info("Unchecking the checkbox.")
        try:
            if self.is_checked():
                LOGGER.info("Checkbox is checked, clicking to uncheck.")
                self.click_element(self.checkbox_btn)
                return True
            else:
                LOGGER.info("Checkbox is already unchecked.")
                return False
        except Exception as e:
            LOGGER.error("Failed to uncheck checkbox with error: {}".format(e))
            raise

    def is_checked(self):
        """
        Checks if the checkbox is currently checked.

            :return: True if the checkbox is checked, False otherwise.
        """
        LOGGER.info("Checking if checkbox is checked.")
        element = self.get_element(*self.locator.get_locator(self.checkbox))
        is_selected = element.get_attribute("data-test-selected")
        is_checked = is_selected == "true"
        LOGGER.info("Checkbox is_checked={}".format(is_checked))
        return is_checked
