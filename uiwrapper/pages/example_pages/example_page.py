from selenium.webdriver.common.by import By

from uiwrapper.actions.container_action import ContainerAction
from uiwrapper.components.check_box import CheckBox
from uiwrapper.components.dropdown import DropDown
from uiwrapper.components.message import Message
from uiwrapper.components.select import Select
from uiwrapper.components.table import Table
from uiwrapper.components.textbox import TextBox
from uiwrapper.components.toast import Toast
from uiwrapper.config_manager import ConfigManager
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class ExamplPage(ContainerAction):
    def __init__(
        self, selenium_helper, ta_name, rest_helper=None, is_open: bool = True
    ) -> None:
        """
        Interact with Event Input of TA.

            :param selenium_helper: An instance of Selenium helper.
            :param rest_helper: Instance to interact with splunk management endpoint.
            :param ta_name: name of the addon.
        """
        container = {"container": [None, ' div[role="main"]']}
        super().__init__(selenium_helper.driver, container, True)
        self.selenium_helper = selenium_helper
        self.rest_url = selenium_helper.splunk.get("splunk_rest_uri")
        self.ta_name = ta_name

        if rest_helper:
            self.config_manager = ConfigManager(
                selenium_helper.splunk.get("splunk_username"),
                selenium_helper.splunk.get("splunk_password"),
                self.rest_url,
            )

        if selenium_helper:
            self.index = Select(
                driver=self.driver,
                name="index",
                value="index",
                by=None,
                index=True,
                searchable=True,
                single_select=True,
            )
            self.account = Select(
                driver=self.driver,
                name="global_account",
                value="global_account",
                by=None,
                searchable=True,
                single_select=True,
            )
            self.input_name = TextBox(self.driver, "name", "name")
            self.interval = TextBox(self.driver, "interval", "interval")
            self.page_title = Message(
                self.driver, "title", '[data-test="column"] .pageTitle', None
            )
            self.page_subtitle = Message(
                self.driver, "subtitle", '[data-test="column"] .pageSubtitle', None
            )
            self.input_container_title = Message(
                self.driver,
                "container_title",
                '[data-test="header"] [data-test="title"]',
                None,
            )
            self.table = Table(self.driver, container)
            if is_open:
                self.open()

    def open(self):
        """This method is used to open the addon specific page"""
        LOGGER.info("Opening page")
        try:
            self.driver.get(
                "{}/en-US/app/{}/inputs".format(
                    self.selenium_helper.splunk.get("splunk_web_uri"), self.ta_name
                )
            )
            self.wait_for_element_invisible("wait-spinner")
            self.wait_for_element("container")
        except Exception as e:
            LOGGER.error("Failed to open input page: {}".format(e))
            raise

    def _get_input_mgmt_url(self):
        return "{}/servicesNS/nobody/{}/INPUT_URL".format(
            self.rest_url, self.ta_name
        )

    def _get_account_mgmt_url(self):
        return "{}/servicesNS/nobody/{}/ACCOUNT_URL".format(
            self.rest_url, self.ta_name
        )
