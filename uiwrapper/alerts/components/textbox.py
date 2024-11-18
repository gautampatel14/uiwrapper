import traceback
from typing import Optional

from selenium.webdriver.common.keys import Keys

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertTextBox(AlertBaseComponent):
    def __init__(
        self, driver, name: str, value: str, by: Optional[str] = None, textarea=False
    ):
        LOGGER.info("Adding TextBox: {}".format(name))
        self.name = name
        self.textarea = textarea
        alert_locator = (
            {name: [by, value + " textarea"]}
            if self.textarea
            else {name: [by, value + " input"]}
        )
        super().__init__(driver, alert_locator)

    def set_value(self, text):
        """
        Set the value in text box.
            :params text: The text to enter in alert textbox.
        """
        try:
            self.wait_for_element_clickable(self.name)
            self.remove_text()
            self.enter_text(self.name, text)
            LOGGER.info("Set value '{}' in text box.".format(text))
        except Exception as e:
            LOGGER.error(
                "Failed to set value in TextBox: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            raise

    def get_value(self):
        """
        Retrieves the current value of the text box.

            :return: The current value of the text box.
        """
        try:
            input_element = self.get_element(*self.locator.get_locator(self.name))
            value = input_element.get_attribute("value").strip()
            return value
        except Exception as e:
            LOGGER.error(
                "Failed to get value from TextBox: {}\nTraceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            raise

    def remove_text(self):
        """
        Clears the text from the text box.
        """
        try:
            element = self.get_element(*self.locator.get_locator(self.name))
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
            element.clear()
            LOGGER.info("Text box text cleared.")
            return True
        except Exception as e:
            LOGGER.error(
                "Failed to clear text in TextBox: {}\nTraceback: {}".format(
                    e,
                    traceback.format_exc(),
                )
            )
            raise

    def is_editable(self):
        """
        Checks if the text box is editable.

            :return: True if the text box is editable, False otherwise.
        """
        try:
            self.wait_for_element(self.name)
            input_element = self.get_element(*self.locator.get_locator(self.name))
            editable = not (
                input_element.get_attribute("disabled")
                or input_element.get_attribute("readonly")
            )
            LOGGER.info("Text box is editable: {}".format(editable))
            return editable
        except Exception as e:
            LOGGER.error(
                "Failed to check if TextBox is editable: {}\nTraceback: {}".format(
                    e,
                    traceback.format_exc(),
                )
            )
            raise

    def get_placeholder(self):
        """
        Retrieves the placeholder text of the text box.

            :return: The placeholder text of the text box.
        """
        try:
            input_element = self.get_element(*self.locator.get_locator(self.name))
            placeholder = input_element.get_attribute("placeholder").strip()
            LOGGER.info("Retrieved placeholder '{}' from text box.".format(placeholder))
            return placeholder
        except Exception as e:
            LOGGER.error(
                "Failed to get placeholder from TextBox: {}\nTraceback: {}".format(
                    e,
                    traceback.format_exc(),
                )
            )
            raise

    def textbox_type(self):
        """
        Retrieves the type of the text box.

            :return: The type of the text box (e.g., 'text', 'password').
        """
        input_element = self.get_element(*self.locator.get_locator(self.name))
        datatype = input_element.get_attribute("type").strip()
        LOGGER.info("textbox type: {}".format(datatype))
        return datatype
