from typing import Optional

from uiwrapper.actions.component_action import ComponentAction
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Tabs(ComponentAction):
    """
    A class for interacting with tab elements on a web page using Selenium WebDriver.
    """

    TABS_BAR = '[data-test="tab-bar"]'
    TABS_LOCATOR = ' [data-test="tab"]'
    LABEL_LOCATOR = ' [data-test="label"]'
    SELECT_TAB_LOCATOR = '[data-test-tab-id="{}"]'

    def __init__(self, driver, name: str, value: str, by: Optional[str] = None):
        """
        Initializes the Tabs with the provided WebDriver, name, value, and optional locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the tab element.
            :param value: The value used to locate the tab element.
            :param by: The type of locator to use. Defaults to None.
        """
        container = {
            "tab_bar_container": [None, self.TABS_BAR],
            "config-wait-spinner": [
                None,
                '[id="{}Tab"] [data-test="wait-spinner"]'.format(value),
            ],
        }
        super().__init__(driver, container)

        self.select_tab = name + "_select"
        self.tab_bar_name = name + "_tab_bar"
        self.tab_label_name = name + "_tab_label"
        self.select_tab = self.SELECT_TAB_LOCATOR.format(value)
        self.label = self.TABS_LOCATOR + self.select_tab + self.LABEL_LOCATOR

        tabs_locators = {
            self.tab_bar_name: [by, self.TABS_BAR],
            self.tab_label_name: [by, self.label],
            self.select_tab: [by, self.select_tab],
        }

        self.locator.update_locaters(tabs_locators)

    def open(self):
        """
        Opens the specified tab by clicking on it.
        """
        LOGGER.info("Opening tab with name={}".format(self.select_tab))
        self.wait_for_element("tab_bar_container")
        self.click_element(self.select_tab)
        self.wait_for_element_invisible("config-wait-spinner")

    def get_tab_label(self):
        """
        Retrieves the label of the currently selected tab.

        :return: The label text of the selected tab.
        """
        LOGGER.info("Getting tab label for name={}".format(self.select_tab))
        self.wait_for_element("tab_bar_container")
        return self.get_text(self.tab_label_name)

    def get_all_tabs(self):
        tabs = []
        for tab in self._find_elements(*self.locator.get_locator(self.TABS_LOCATOR)):
            tabs.append(tab.text.strip())

        return tabs
