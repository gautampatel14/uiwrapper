from uiwrapper.actions.component_action import ComponentAction
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Base(ComponentAction):
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
        self.name = list(container)[0]
        self.value = container[self.name][1]
        new_locators = {
            "label_component": [None, self.value + ' [id][data-test="label"]'],
            "tooltip": [None, ' [data-test="screen-reader-content"]'],
            "icon": [None, self.value + ' [data-test="tooltip"]'],
            "help": [None, self.value + ' [data-test="help"]'],
        }
        container.update(new_locators)
        super().__init__(driver, container)

    def get_help_text(self) -> str:
        """
        Retrieves the text content from the help component.

            :return: The text content of the help component.
        """
        LOGGER.info("Getting help text.")
        return self.get_element_text(
            self.get_element(*self.locator.get_locator("help"))
        )

    def get_tooltip_text(self) -> str:
        """
        Hovers over the icon component to reveal the tooltip and retrieves its text content.

            :return: The text content of the tooltip component.
        """
        LOGGER.info("Getting tooltip text.")
        self._hover_element("icon")
        self.wait_for_element("tooltip")
        return self.get_element_text(
            self.get_element(*self.locator.get_locator("tooltip"))
        )

    def get_label(self) -> str:
        """
        Retrieves the text content from the label component.

            :return: The text content of the label component.
        """
        LOGGER.info("Getting label text.")
        self.wait_for_element("label_component")
        return self.get_element_text(
            self.get_element(*self.locator.get_locator("label_component"))
        )
