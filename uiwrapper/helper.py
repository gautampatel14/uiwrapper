import os
import sys
import traceback

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from uiwrapper.log.logging import Logger
from uiwrapper.pages.login_page import LoginPage

LOGGER = Logger.get_logger("uiwrapper")


class WebDriverHelper:
    """
    A helper class for setting up and managing the WebDriver, including logging into the splunk instance.
    """

    def __init__(self, config):
        """
        Initializes the WebDriverHelper with the provided configuration.

            :param config (Config): Configuration object with settings for the test session.
        """
        self.config = config
        self.browser = config._browser
        self.remote_host = os.getenv("REMOTE_HOST")
        self.headless = config._headless
        self.splunk = config._splunk
        self.driver = self.setup_driver()
        self.login()

    def setup_driver(self):
        """
        Sets up the WebDriver based on the specified browser and headless mode.

            :returns webdriver: The initialized WebDriver instance.
            :raise ValueError: if the specified browser is unsupported.
        """
        LOGGER.info("Setting up the WebDriver")
        try:
            options = self.get_browser_options()
            if self.browser == "chrome":
                return self.setup_chrome_driver(options)
            elif self.browser == "firefox":
                return self.setup_firefox_driver(options)
            elif self.browser == "edge":
                return self.setup_edge_driver(options)
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")

        except WebDriverException as e:
            LOGGER.error(
                "WebDriverException: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            raise
        except Exception as e:
            LOGGER.error(
                "Error occurred while setting up the WebDriver for {}: {}\nTraceback: {}".format(
                    self.browser, e, traceback.format_exc()
                )
            )
            raise

    def login(self):
        """
        Logs into the application using the provided Splunk credentials.

            :raises exception: If an error occurs during the login process.
        """
        try:
            self.driver_session = self.driver.session_id
            login_page = LoginPage(self)
            login_page.login(
                self.splunk.get("splunk_username"),
                self.splunk.get("splunk_password"),
            )
        except Exception as e:
            self.driver.quit()
            LOGGER.error(
                "An unexpected error occurred during login: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            raise

    def get_browser_options(self):
        """
        Sets up and returns browser-specific WebDriver options.

            :return: Options configured for the specified browser.
            :raises ValueError: if the specified browser is unsupported.
        """
        LOGGER.info(f"Configuring options for {self.browser}")
        options = None

        try:
            if self.browser == "chrome":
                from selenium.webdriver.chrome.options import Options

                options = Options()
                options.set_capability("browserName", "chrome")
            elif self.browser == "firefox":
                from selenium.webdriver.firefox.options import Options

                options = Options()
                options.set_capability("browserName", "firefox")
            elif self.browser == "edge":
                from selenium.webdriver.edge.options import Options

                options = Options()
                options.set_capability("browserName", "MicrosoftEdge")
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")

            options.add_argument("--ignore-ssl-errors=yes")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-insecure-localhost")

            if self.headless:
                options.add_argument("--headless")
                options.add_argument("--window-size=1280,768")

            return options
        except Exception as e:
            LOGGER.error(
                "Error occurred while setting up browser options for {}: {}\nTraceback: {}".format(
                    self.browser, e, traceback.format_exc()
                )
            )
            raise

    def setup_chrome_driver(self, options):
        """
        Set up the chrome browser
            :param options: browser options arguments.
            :returns webdriver: return the chrome webdriver

        """
        from selenium.webdriver.chrome.service import Service

        if self.remote_host:
            return webdriver.Remote(
                command_executor=f"{self.remote_host}:4444/wd/hub",
                options=options,
            )
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            driver_path = os.path.join(current_dir, "drivers", "chromedriver")
            service = Service(executable_path=driver_path)
            return webdriver.Chrome(service=service, options=options)

    def setup_firefox_driver(self, options):
        """
        Set up the firefox browser
            :param options: browser options arguments.
            :returns webdriver: return the firefox webdriver

        """
        from selenium.webdriver.firefox.service import Service

        if self.remote_host:
            return webdriver.Remote(
                command_executor=f"{self.remote_host}:4444/wd/hub",
                options=options,
            )
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            driver_path = os.path.join(current_dir, "drivers", "geckodriver")
            service = Service(executable_path=driver_path)
            return webdriver.Firefox(service=service, options=options)

    def setup_edge_driver(self, options):
        """
        Set up the edge browser. only run in local.
            :param options: browser options arguments.
            :returns webdriver: return the edge webdriver

        """
        from selenium.webdriver.edge.service import Service

        if sys.platform.startswith("darwin"):
            platform = "MAC"
            driver_file = "msedgedriver"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            platform = "WINDOWS"
            driver_file = "msedgedriver.exe"
        else:
            platform = "LINUX"
            driver_file = "msedgedriver"

        current_dir = os.path.dirname(os.path.abspath(__file__))
        driver_path = os.path.join(current_dir, "drivers", driver_file)
        service = Service(executable_path=driver_path)

        return webdriver.Edge(service=service, options=options)


class RestHandlerHelper:
    """ """

    def __init__(self, config) -> None:
        """ """
        self.config = config
        self.rest_uri = config._splunk.get("splunk_rest_uri")
        self.username = config._splunk.get("splunk_username")
        self.password = config._splunk.get("splunk_password")
        self.login()

    def login(self):
        try:
            url = self.rest_uri + "/services/auth/login?output_mode=json"
            LOGGER.info("URL={}".format(url))
            response = requests.post(
                url=url,
                data={"username": self.username, "password": self.password},
                verify=False,
            )
            response = response.json()
            self.session_key = str(response["sessionKey"])
            LOGGER.info("sessionKey: {}".format(self.session_key))
        except Exception as e:
            LOGGER.error(
                "Unable to Connect with Splunk Management instance \nTraceback: {}".format(
                    traceback.format_exc()
                )
            )
            raise e


def get_updated_message(message):
    """
    :return: This message return clear message.
    """
    return message.strip().replace(" ", "").replace('"', "").lower()
