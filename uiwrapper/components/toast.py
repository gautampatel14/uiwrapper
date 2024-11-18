import traceback

from uiwrapper.components.base import Base
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Toast(Base):
    """
    Represents a toast message element on a web page.
    """

    TOAST_CONTAINER = '[data-test="toast-messages"]'
    TOAST_MESSAGE = ' [data-test="toast"] [data-test="toast-message"]'

    def __init__(self, driver, name: str):
        """
        Initializes a Toast instance.

            :param driver: The WebDriver instance for interacting with the web page.
            :param name: The name of the toast message instance.
        """
        self.name = name
        self.toast_message_name = self.name + "_toast_message"
        toast_container = {"toast_container": [None, self.TOAST_CONTAINER]}
        super().__init__(driver, toast_container)
        toast_locators = {
            self.toast_message_name: [None, self.TOAST_CONTAINER + self.TOAST_MESSAGE],
        }
        self.locator.update_locaters(toast_locators)

    def get_toast_message(self):
        """
        Retrieves the text content of the toast message.

            :return: The text content of the toast message.
        """
        try:
            self.wait_for_element("toast_container")
            toast_message = self.get_element(
                *self.locator.get_locator(self.toast_message_name)
            )
            return toast_message.text
        except Exception as e:
            LOGGER.error(
                "Failed to retrieve toast message: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            return ""
