from uiwrapper.actions.container_action import ContainerAction
from uiwrapper.components.select import Select
from uiwrapper.components.tabs import Tabs
from uiwrapper.components.toast import Toast
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Logging(ContainerAction):
    """
    A class representing a logging configuration page handler.
    """

    def __init__(self, selenium_helper, ta_name, rest_helper=None) -> None:
        """
        Interact with Logging page of TA.

            :param selenium_helper (object): An instance of Selenium helper.
            :param ta_name (str, optional): The name of the TA for Splunk.
        """
        self.selenium_helper = selenium_helper
        container = {"container": [None, ' div[id="loggingTab"]']}
        super().__init__(selenium_helper.driver, container)
        self.ta_name = ta_name
        if selenium_helper:
            self.select_logging = Select(
                driver=self.driver,
                name="logging",
                single_select=True,
                value="loglevel",
            )
            self.logging_tab = Tabs(self.driver, "logging", "logging", None)
            self.toast = Toast(self.driver, "logging_toast")
            self.open()

    def open(self):
        """
        Opens the logging configuration page in the browser.
        """
        try:
            LOGGER.info("Opening logging configuration page")
            self.driver.get(
                "{}/en-US/app/{}/configuration".format(
                    self.selenium_helper.splunk.get("splunk_web_uri"), self.ta_name
                )
            )
            self.logging_tab.open()
        except Exception as e:
            LOGGER.error("Failed to open logging configuration page: {}".format(e))
            raise
