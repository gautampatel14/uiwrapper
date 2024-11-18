from uiwrapper.alerts.actions.alert_action_component import AlertComponentAction
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertBaseComponent(AlertComponentAction):
    """
    A base class for interacting with common UI components using Selenium WebDriver.
    """

    def __init__(self, driver, container: dict):
        """
        Initializes the Base class with the provided WebDriver and container locators.
        Sets up additional locators for label, tooltip, icon, and help components.

            :param driver: The WebDriver instance for interacting with the browser.
            :param container: A dictionary containing locators for the container elements.
        """
        super().__init__(driver, container)

        self.locator.update_locaters(
            {
                "label_component": [None, " .control-label"],
                "help": [None, " .help-block"],
            }
        )

    def get_alert_help_text_list(self) -> list:
        """
        Retrieves the text content from the help component.

            :return: The list of text content of the help component.
        """
        values = []
        LOGGER.info("Getting help text.")
        for help in self._find_elements(*self.locator.get_locator("help")):
            values.append(help.text)

        # val = self.get_text("help")
        LOGGER.info("Help texts: {}".format(values))
        return values

    def get_alert_labels_list(self) -> list:
        """
        Retrieves the text content from the label component.

            :return: The list of text content of the label component.
        """
        LOGGER.info("Getting label text.")
        values = []
        self.wait_for_element("label_component")
        for label in self._find_elements(*self.locator.get_locator("label_component")):
            values.append(label.text)

        LOGGER.info("Labels: {}".format(values))
        return values
