import traceback
from typing import Optional

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertCheckbox(AlertBaseComponent):
    def __init__(self, driver, name: str, value: str, by: Optional[str] = None):
        """
        Initializes the DropDown with the provided WebDriver, name, value, locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the Checkbox.
            :param value: The value used to locate the Checkbox.
            :param by: The type of locator to use. Defaults to None.
        """
        container = {name: [by, value]}
        super().__init__(driver, container)

        self.name = name
        LOGGER.info("Adding Checkbox: {}".format(name))
        self.locator.update_locaters(
            {
                name: [by, value],
                "checkbox_btn": [None, value + " .checkbox a.btn"],
                "icon_checked": [
                    None,
                    value + ".checkbox a.btn .icon-check",
                ],  # visible only if checkbox is checked.
            }
        )

    def check(self):
        """
        Checks the checkbox if it is not already checked.

            :return: True if the checkbox was checked, False if it was already checked.
            :raises Exception: If an error occurs while checking the checkbox.
        """
        try:
            self.wait_for_element("checkbox_btn")
            if not self.is_checked():
                LOGGER.info("Checkbox is not checked, clicking to check.")
                self.click_element("checkbox_btn")
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
                self.click_element("checkbox_btn")
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
        element = self.get_element(*self.locator.get_locator(self.name))
        return element.get_attribute("aria-checked") == "true"
