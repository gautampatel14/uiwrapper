import re
import traceback
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from uiwrapper.actions.locator import Locator
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertComponentAction:
    """
    A helper class for interacting with web page components using Selenium WebDriver.
    """

    def __init__(self, driver, element_locators={}):
        """
        Initializes the ComponentAction with the provided WebDriver.
            :param driver: The instance of the Selenium WebDriver for interacting with the browser.
            :param element_locators: A dictionary of existing locators.
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.action = ActionChains(driver)
        self.locator = Locator(element_locators)

    def get_element(self, by: str, value: str):
        """
        Gets a web element using the specified locator.

            :param by: The strategy to locate the element.
            :param value: The locator value.
            :return: The found web element.
            :raises TimeoutException: If the element is not found within the timeout.
        """
        msg = "Element with by={} and value={} not found.".format(by, value)
        return self.wait.until(EC.presence_of_element_located((by, value)), msg)

    def _find_element(self, element, locator: str):
        """
        Finds a single web element within a specified parent element using the locator.

            :param element: The parent web element.
            :param locator: The locator key.
            :return: The found web element.
        """
        return element.find_element(*self.locator.get_locator(locator))

    def _find_elements(self, by: str, value: str):
        """
        Finds multiple web elements using the specified locator.

            :param by: The strategy to locate the elements.
            :param value: The locator value.
            :return: A list of found web elements.
        """
        try:
            return self.driver.find_elements(by, value)
        except Exception:
            LOGGER.error(
                "Elements with by={} and value={} not found.".format(by, value)
            )
            return []

    def click_element(self, locator: str):
        """
        Clicks on a web element identified by the specified locator.

            :param locator: The name/key of the locator.
            :raises Exception: If the element is not clickable.
        """
        try:
            element = self.wait_for_element_clickable(locator)
            if element:
                element.click()
            else:
                LOGGER.error("Element with locator '{}' is not found.".format(locator))
        except Exception as e:
            LOGGER.error(
                "Error clicking element with locator '{}', error: {}\nTraceback: {}".format(
                    locator, e, traceback.format_exc()
                )
            )
            raise

    def enter_text(self, locator: str, text: str):
        """
        Enters text into a web element identified by the specified locator.

            :param locator: The name/key of the locator.
            :param text: The text to enter into the element.
            :raises Exception: If there is an error entering text into the element.
        """
        try:
            by, value = self.locator.get_locator(locator)
            LOGGER.info(
                "Entering value with locator: {}, by={} and value={}".format(
                    locator, by, value
                )
            )
            element = self.get_element(by, value)
            if value != "password":
                element.clear()
            element.send_keys(text)
        except Exception as e:
            LOGGER.error(
                "Error entering text with locator '{}', by={} and value={} error: {}\nTraceback: {}".format(
                    locator, by, value, e, traceback.format_exc()
                )
            )
            raise

    def wait_for_element(self, locator: str, timeout: Optional[int] = None):
        """
        Waits for a web element to be visible using the specified locator.

            :param locator: The name/key of the locator.
            :param timeout: The maximum wait time in seconds. Defaults to 15.
            :return: The found web element.
            :raises TimeoutException: If the element is not visible within the timeout.
        """
        LOGGER.info("Waiting for element: {}".format(locator))
        by, value = self.locator.get_locator(locator)
        msg = "Element with locator={}, by={} and value={} is not visible".format(
            locator, by, value
        )
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.visibility_of_element_located((by, value)), msg)

    def wait_for_element_invisible(self, locator: str, timeout: Optional[int] = None):
        """
        Waits for a web element to become invisible using the specified locator.

            :param locator: The name/key of the locator.
            :param timeout: The maximum wait time in seconds. Defaults to None.
            :return: True if the element is invisible, False otherwise.
        """
        by, value = self.locator.get_locator(locator)
        msg = "Element with locator={}, by={} and value={} did not become invisible.".format(
            locator, by, value
        )
        LOGGER.info(
            "Waiting for element to become invisible: locator={}, by={} and value={}".format(
                locator, by, value
            )
        )
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        return wait.until(EC.invisibility_of_element_located((by, value)), msg)

    def wait_for_element_clickable(self, locator: str):
        """
        Waits for a web element to be clickable using the specified locator.

            :param locator: The name/key of the locator.
            :return: The found web element if clickable, otherwise raises TimeoutException.
        """
        by, value = self.locator.get_locator(locator)
        msg = "Element with locator '{}', by={} and value={} is not clickable.".format(
            locator, by, value
        )
        LOGGER.info(
            "Waiting for element to be clickable: locator={}, by={} and value={}".format(
                locator, by, value
            )
        )
        return self.wait.until(EC.element_to_be_clickable((by, value)), msg)

    def _hover_element(self, locator: str):
        """
        Hovers over a web element identified by the specified locator.

            :param locator: The name/key of the locator.
        """
        by, value = self.locator.get_locator(locator)
        element = self.get_element(by, value)
        LOGGER.info(
            "Hovering over element with locator={}, by={} and value={}".format(
                locator, by, value
            )
        )
        self.action.move_to_element(element).perform()

    def get_text(self, locator: str):
        """
        Retrieves the text of a web element identified by the specified locator.

            :param locator: The name/key of the locator.
            :return: The text content of the web element.
        """
        text_element = self.get_element(*self.locator.get_locator(locator))
        element_text = self.driver.execute_script(
            """
            var label = arguments[0];
            var childSpan = label.querySelectorAll('span[data-test="screen-reader-content"]');
            childSpan.forEach(function(span) {
                span.remove();
                });
            return label.textContent.trim();
            """,
            text_element,
        )
        return (
            element_text
            if element_text.lower() != ""
            else "element text not found of locator={}".format(locator)
        )

    def get_element_text(self, element):
        """
        Gets the Inner text of the web element.

            :param element: The web element we are getting text from.
            :return: The text of the web element.
        """
        inner_text = element.get_attribute("innerText")
        text = re.sub(r"\s+", " ", inner_text).strip()
        return text

    def get_updated_message(self, text: str):
        """
        Returns the message without spaces and double quotes.

            :param text: The text to be updated.
            :return: The updated message.
        """
        return text.strip().replace(" ", "").replace('"', "").lower()
