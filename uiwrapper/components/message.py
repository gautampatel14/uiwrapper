from typing import Optional

from uiwrapper.components.base import Base
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Message(Base):
    """
    A class for interacting with message elements on a web page using Selenium WebDriver.
    """

    def __init__(self, driver, name: str, value: str, by: Optional[str] = None):
        """
        Initializes the Message with the provided WebDriver, name, value, and locator type.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the message element.
            :param value: The value used to locate the message element.
            :param by: The type of locator to use. Defaults to None.
        """
        self.name = name
        container = {name: [by, value]}
        super().__init__(driver, container)

    def get_message(self):
        """
        Retrieves the message text from the message element.

            :return: The text content of the message element.
        """
        LOGGER.info("Getting message text.")
        message_element = self.get_element(*self.locator.get_locator(self.name))
        return message_element.text.strip()

    def wait_for_message_cycle(self, timeout: int = 10):
        """
        Waits for the message element to appear and then disappear, and retrieves its text content.

            :param timeout: The maximum wait time in seconds. Defaults to 10.
            :return: The text content of the message element after it appears.
            :raises Exception: If there is an error during the wait or retrieval process.
        """
        try:
            LOGGER.info("Waiting for message cycle with timeout={}".format(timeout))
            self.wait_for_element(self.name, timeout=timeout)
            text = self.get_message()
            self.wait_for_element_invisible(self.name, timeout=timeout)
            LOGGER.info("Message cycle completed with text: '{}'".format(text))
            return text
        except Exception as e:
            LOGGER.error("Error during message cycle: {}".format(e))
            raise e
