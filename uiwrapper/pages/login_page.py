from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from uiwrapper.actions.component_action import ComponentAction
from uiwrapper.log.logging import Logger
from uiwrapper.pages.base_page import BasePage

LOGGER = Logger.get_logger("uiwrapper")


class LoginPage(BasePage):
    """
    LoginPage handles the interactions with the login page of the Splunk application.

    Attributes:
        selenium_helper (SeleniumHelper): An instance of SeleniumHelper.
        component_instance (Component): An instance of Component for interacting with page elements.
    """

    def __init__(self, selenium_helper) -> None:
        """
        Initializes the LoginPage with the provided selenium_helper.

            :param selenium_helper: Helper for selenium actions and configurations.
        """
        LOGGER.info("Initializing LoginPage with selenium_helper")
        super().__init__(selenium_helper.driver, selenium_helper.splunk)

        login_locators = {
            "splunk_username": [By.ID, "username"],
            "splunk_password": [By.ID, "password"],
            "home": [By.CSS_SELECTOR, 'a[data-action="home"]'],
        }
        self.component_instance = ComponentAction(
            selenium_helper.driver, login_locators
        )

    def login(self, username, password):
        """
        Performs login action by entering the username and password.

            :param username: The username for login.
            :param password: The password for login.
        """
        LOGGER.info("Attempting to login with username: {}".format(username))
        self.component_instance.enter_text("splunk_username", username)
        self.component_instance.enter_text("splunk_password", password)
        self.component_instance.enter_text("splunk_password", Keys.RETURN)
        self.component_instance.wait_for_element("home", 15)
        LOGGER.info("Login successful.")
