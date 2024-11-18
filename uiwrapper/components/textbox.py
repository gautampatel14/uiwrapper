import traceback
from typing import Optional

from selenium.webdriver.common.keys import Keys

from uiwrapper.components.base import Base
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class TextBox(Base):
    """
    A helper class for interacting with text box components on a web page.
    """

    CONTROL_GROUP = '[data-test="control-group"][data-name="{}"]'

    def __init__(self, driver, name: str, value: str, by: Optional[str] = None):
        """
        Initializes the TextBox with the provided WebDriver and locator.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the text box element.
            :param value: The value used to locate the text box element.
            :param by: The type of locator to use. Defaults to None.
        """
        self.name = name
        self.select_value = self.CONTROL_GROUP.format(value)
        textbox_container = {"text_box_group": [by, self.select_value]}
        super().__init__(driver, textbox_container)

        self.locator.update_locaters(
            {
                self.name: [
                    by,
                    self.select_value + ' [data-test="controls"] input',
                ]
            }
        )

    def set_value(self, text: str):
        """
        Sets the specified text in the text box.

            :param text: The text to enter in the text box.
        """
        try:
            self.wait_for_element_clickable(self.name)
            self.remove_text()
            self.enter_text(self.name, text)
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

    def get_placeholder(self):
        """
        Retrieves the placeholder text of the text box.

            :return: The placeholder text of the text box.
        """
        try:
            input_element = self.get_element(*self.locator.get_locator(self.name))
            placeholder = input_element.get_attribute("placeholder").strip()
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
        return datatype
