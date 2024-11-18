from selenium.webdriver.common.by import By

from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Locator:
    """
    A class for managing web element locators.
    """

    def __init__(self, existing_locators: dict):
        """
        Initializes the Locator with an empty dictionary for storing locators.

            :param existing_locators: Dictionary of existing locators.
        """
        existing_locators = {
            key: [By.CSS_SELECTOR if val[0] is None else val[0], val[1]]
            for key, val in existing_locators.items()
        }
        self.locators = existing_locators

    def get_locator(self, name: str) -> list:
        """
        Get the locator tuple [by, value] by its name.

            :param name: The name/key of the locator.
            :return: The locator tuple [by, value].
        """
        locator = self.locators.get(name, [])
        LOGGER.info(
            "Getting locator={} with by={}, value={}".format(
                name, locator[0], locator[1]
            )
        )
        return locator

    def get_all_locators(self):
        """
        Get all locators stored in the Locator object.

            :return: Dictionary containing all locators stored.
        """
        LOGGER.info("Retrieved all locators.")
        return self.locators

    def update_locaters(self, new_locators: dict):
        """
        Updates the locators with new elements.

            :param new_locators: Dictionary of new locators to update.
        """
        LOGGER.info("Updating element: {}".format(new_locators))
        updated_locators = {
            key: [By.CSS_SELECTOR if val[0] is None else val[0], val[1]]
            for key, val in new_locators.items()
        }
        self.locators.update(updated_locators)
