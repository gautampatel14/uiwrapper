import traceback

from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class BasePage:
    """
    A helper class for managing page interactions in the web application.

    Attributes:
        driver (webdriver): The WebDriver instance for interacting with the browser.
        splunk (dict): Dictionary containing Splunk connection information.
        is_open (bool): Flag to indicate if the page is open.
    """

    def __init__(self, driver, splunk):
        """
        Initializes the PageHelper with the provided WebDriver and Splunk information.

            :param driver (webdriver): The WebDriver instance for interacting with the browser.
            :param splunk (dict): Dictionary containing Splunk connection information.
        """
        self.driver = driver
        self.splunk = splunk
        self.is_open = False
        # use full while running the test cases in session scope to keep connection alive.
        if not self.is_open:
            LOGGER.info("Opening the Splunk Login Page.")
            self.is_open = True
            self.open()

    def open(self):
        """
        Opens the Splunk Login Page using the URL provided in the Splunk information.
        """
        try:
            LOGGER.info(
                "Opening Splunk Login Page at URL: {}".format(
                    self.splunk.get("splunk_web_uri")
                )
            )

            self.driver.get(self.splunk.get("splunk_web_uri"))
        except Exception as e:
            LOGGER.error(
                "Failed to open Splunk Login Page: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            raise

    def close(self):
        """
        Closes the current page by quitting the WebDriver instance.
        """
        try:
            LOGGER.info("Closing the browser.")
            self.driver.quit()
            self.is_open = False
            LOGGER.info("Browser closed successfully.")
        except Exception as e:
            LOGGER.error(
                "Failed to close the browser: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            raise e
