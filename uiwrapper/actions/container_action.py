import traceback
from typing import Optional

from selenium.webdriver.common.by import By

from uiwrapper.actions.component_action import ComponentAction
from uiwrapper.components.button import Button
from uiwrapper.components.dropdown import DropDown
from uiwrapper.components.message import Message
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class ContainerAction(ComponentAction):
    """
    ContainerAction handles actions for a UI container component in a web application.
    """

    MODAL = ' [data-test="modal"]'

    def __init__(
        self,
        driver,
        element_locators: dict,
        multi_input: Optional[bool] = False,
        single_input: Optional[bool] = False,
    ) -> None:
        """
        Initializes the ContainerAction with the given web driver and element_locators.

            :param driver: The web driver instance.
            :param element_locators: A dictionary of element_locators for the container elements.
            :param multi_input: A bool variable indicating that add on support multi input or not. Default is set to false.
            :param single_input: A bool variable indicating that add on support single input or not. Default is set to false.
        """
        super().__init__(driver, element_locators)
        self.name = list(element_locators)[0]
        self.value = element_locators[self.name][1]
        self.is_multi_input = multi_input
        self.is_single_input = single_input

        self.locator.update_locaters(
            {
                "wait-spinner": [None, '[data-test="wait-spinner"]'],
                "open_modal": [None, self.MODAL],
            }
        )
        if self.is_multi_input:
            self.create_multi_input_btn = DropDown(
                self.driver, "add_input_btn", "addInputBtn", By.ID, True
            )
        elif self.is_single_input:
            self.create_input_btn = Button(
                self.driver, "add_input_btn", "addInputBtn", By.ID
            )
        self.save_btn = Button(self.driver, "save_btn", self.MODAL + " .saveBtn", None)
        self.edit_btn = Button(self.driver, "edit_btn", self.MODAL + " .editBtn", None)
        self.delete_btn = Button(
            self.driver,
            "delete_btn",
            self.MODAL + ' button[label="Delete"]',
            By.CSS_SELECTOR,
        )
        self.close_btn = Button(
            self.driver, "close_btn", self.MODAL + ' button[data-test="close"]', None
        )
        self.add_btn = Button(
            self.driver,
            "add_btn",
            self.value + ' button[data-test="button"][label="Add"]',
            None,
        )
        self.cancel_btn = Button(
            self.driver,
            "cancel_btn",
            self.MODAL + ' button[data-test="button"][label="Cancel"]',
            None,
        )
        self.config_save = Button(
            self.driver, "save_btn", self.value + " .saveBtn", None
        )
        self.error_container = Message(
            self.driver,
            "error_msg",
            '[data-test-type="error"][data-test="message"] div[data-test="content"]',
            None,
        )

    def add(self, value: Optional[str] = None):
        """
        Opens the container by clicking the add button and waiting for the container element.

            :return: True if the container is successfully opened.
        """
        try:
            if self.is_multi_input and value:
                self.create_multi_input_btn.select(value)
            elif self.is_single_input:
                self.create_input_btn.click()
            else:
                self.add_btn.click()
            self.wait_for_element("open_modal")
            return True
        except Exception as e:
            LOGGER.error(
                "Error while clicking add button. Error: {}\n Traceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            return False

    def close(self):
        """
        Closes the container by clicking the close button and waiting for the container element.

            :return: True if the container is successfully closed.
        """
        try:
            self.close_btn.click()
            self.wait_for_element_invisible("open_modal")
            return True
        except Exception as e:
            LOGGER.error(
                "Error while clicking close button. Error: {}\n Traceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            return False

    def save(self):
        """
        Saves changes in the container by clicking the save button and waiting for the container element.

            :return: True if the changes are successfully saved.
        """
        try:
            LOGGER.info("Saving.....")
            self.save_btn.click()
            error_msg = ""
            try:
                error_msg = self.error_container.get_message()
            except:
                pass
            LOGGER.info("ERROR: {}".format(error_msg))
            if error_msg != "":
                return error_msg
            self.wait_for_element_invisible("open_modal", 60)
            return True
        except Exception as e:
            LOGGER.error(
                "Error while clicking save button. Error: {}\n Traceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            return False

    def cancel(self):
        """
        Cancels the current action in the container by clicking the cancel button and waiting for the container element.

            :return: True if the action is successfully canceled.
        """
        try:
            self.cancel_btn.click()
            self.wait_for_element_invisible("open_modal")
            return True
        except Exception as e:
            LOGGER.error(
                "Error while clicking cancel button. Error: {}\n Traceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            return False

    def save_config(self):
        """
        Saves the configuration changes in the container by clicking the save button and waiting for the container element.

            :return: True if the configuration changes are successfully saved.
        """
        try:
            self.config_save.click()
            self.wait_for_element(self.name)
            return True
        except Exception as e:
            LOGGER.error(
                "Error while clicking save button. Error: {}\n Traceback: {}".format(
                    e, traceback.format_exc()
                )
            )
            return False

    def error_message(self):
        """
        Retrieves the error message from the container.

            :return: The error message text.
        """
        return self.error_container.get_message()
