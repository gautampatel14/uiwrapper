import traceback

from selenium.webdriver.common.keys import Keys

from uiwrapper.alerts.actions.alert_action_component import AlertComponentAction
from uiwrapper.alerts.components.button import AlertButton
from uiwrapper.alerts.components.dropdown import AlertDropDown
from uiwrapper.alerts.components.search_box import SearchQueryBox
from uiwrapper.alerts.components.textbox import AlertTextBox
from uiwrapper.components.message import Message
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertContainerAction(AlertComponentAction):
    """
    ContainerAction handles actions for a UI container component in a web application.
    """

    def __init__(self, driver, container: dict) -> None:
        """
        Initializes the ContainerAction with the given web driver and locators.

            :param driver: The web driver instance.
        """
        LOGGER.info("AlertContainerAction")
        super().__init__(driver, container)

        self.locator.update_locaters(
            {
                "wait_btn": [None, ".alert-save-as .btn-save"],
            }
        )

        self.alert_name = AlertTextBox(
            self.driver, "alert_name", "div[data-name=name]", None
        )
        self.description = AlertTextBox(
            self.driver, "alert_desc", "div[data-name=description]", None, True
        )
        self.add_alert_btn = AlertButton(
            self.driver, "new_alert_btn", ".new-alert-button", None
        )
        self.save_btn = AlertButton(
            self.driver, "alert_save", ".alert-save-as .btn-save", None
        )
        self.cancel_btn = AlertButton(
            self.driver, "alert_cancel", ".alert-save-as .btn.cancel", None
        )
        self.close_btn = AlertButton(self.driver, "alert_close", ".close", None)
        self.add_action_dropdown = AlertDropDown(
            self.driver, "alert_add_action", ".add-action-btn", None
        )
        self.search_query = SearchQueryBox(
            self.driver, "alert_search_query_box", ".search-bar-input", None
        )
        self.error_container = Message(
            self.driver,
            "error_msg",
            ".alert-save-as .alert-error",
            None,
        )
        self.got_it_button = AlertButton(
            self.driver, "got_it_button", ".modal-footer .btn-save", None
        )

    def open(self):
        """
        Open the alert add container.
        """
        LOGGER.info("Opening add alert action container.")
        self.add_alert_btn.click()

    def close(self):
        """
        Closes the container by clicking the close button and waiting for the container element.

            :return: True if the container is successfully closed.
        """
        try:
            LOGGER.info("Closing the alert action container")
            self.close_btn.click()
            self.wait_for_element_invisible("wait_btn", 60)
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
            LOGGER.info("Saving the alert actions.")
            self.save_btn.click()
            error_msg = ""
            try:
                error_msg = self.error_container.get_message()
            except:
                pass
            if error_msg != "":
                return error_msg
            self.wait_for_element_invisible("wait_btn", 60)
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
            LOGGER.info("Cancelling the alert action container")
            self.cancel_btn.click()
            self.wait_for_element_invisible("wait_btn", 60)
            return True
        except Exception as e:
            LOGGER.error(
                "Error while clicking cancel button. Error: {}\n Traceback: {}".format(
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

    def _remove_got_it_popup(self):
        try:
            self.got_it_button.click()
        except Exception:
            pass
