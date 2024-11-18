from typing import Optional

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertDropDown(AlertBaseComponent):
    """
    A class for interacting with dropdown elements on a web page using Selenium WebDriver.
    """

    def __init__(
        self,
        driver,
        name: str,
        value: str,
        by: Optional[str] = None,
    ):
        """
        Initializes the DropDown with the provided WebDriver, name, value, locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the dropdown.
            :param value: The value used to locate the dropdown.
            :param by: The type of locator to use. Defaults to None.
        """
        LOGGER.info("Adding Dropdown: {}".format(name))
        container = {name: [by, value]}
        super().__init__(driver, container)
        self.locator.update_locaters(
            {
                "add_action": [None, value + " .dropdown-toggle.btn"],
                "action_name": [None, " .unselected-action span:first-of-type"],
                "alert_menu": [None, ".dropdown-menu.open"],
                "add_actions_container": [None, ".link-label"],
            }
        )

    def get_dropdown_values(self):
        """
        Retrieves all options from the dropdown.
            :return: Returns a list of dropdown values.
        """
        val = []
        self.click_element("add_action")
        self.wait_for_element("alert_menu")

        for action in self._find_elements(*self.locator.get_locator("action_name")):
            val.append(self.get_element_text(action))
        return val

    def select(self, action_name):
        """
        Select the value from the select options.
            :params action_name: the action name to be selected.
        """
        self.click_element("add_action")
        self.wait_for_element("alert_menu")
        for action in self._find_elements(*self.locator.get_locator("action_name")):
            if action_name == self.get_element_text(action):
                action.click()
                return True
        else:
            raise ValueError(
                "Given Alert Action '{}' is not found.".format(action_name)
            )

    def get_add_actions_list(self):
        """
        Retrieves all options from the add_actions list dropdown.
            :return: returns a list of all dropdown values with '.link-label' selector.
        """
        val = []
        self.click_element("add_action")

        for action in self._find_elements(
            *self.locator.get_locator("add_actions_container")
        ):
            val.append(self.get_element_text(action))
        return val
