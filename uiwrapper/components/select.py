import time
import traceback
from typing import Optional

from selenium.webdriver.common.keys import Keys

from uiwrapper.components.base import Base
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class Select(Base):
    """
    A class used to represent a Select UI component which can handle both single and multi-select dropdowns.
    """

    CONTROL_GROUP = '[data-test="control-group"][data-name="{}"]'
    SINGLE_BUTTON_LOCATOR = ' [data-test="select"]'
    MULTI_BUTTON_LOCATOR = ' [data-test="multiselect"] [data-test="textbox"]'
    COMBO_BOX = ' [data-test="combo-box"]'
    SINGLE_SELECTED_LOCATOR = ' [data-test="textbox"]'
    CANCEL_BUTTON_LOCATOR = ' [data-test="clear"]'
    MULTI_SELECTED_LOCATOR = ' [data-test="selected-option"] div[data-test="label"]'
    DESELECTED = ' [data-test="selected-option"] div[data-test="label"]'
    OPTION = ' [data-test="option"]'
    MENU_LOCATOR = ' [data-test="menu"]'
    VALUES_LOCATOR = ' [data-test="option"]'
    POPOVER = '[data-test="popover"]'
    SEARCH_RESULT_LIST = '[data-test="popover"] [data-test="menu"] [data-test="option"] [data-test="label"]'
    SELECTED_TRUE = ' [data-test-selected="true"]'

    def __init__(
        self,
        driver,
        name: str,
        value: str,
        by: Optional[str] = None,
        multi_select: bool = False,
        single_select: bool = False,
        index: bool = False,
        searchable: bool = False,
    ) -> None:
        """
        Initializes the Select with the provided WebDriver, name, value, locator type,
        multi_select, single_select, index, and searchable flag.

            :param driver: The WebDriver instance for interacting with the browser.
            :param name: The name/key of the dropdown.
            :param value: The value used to locate the dropdown.
            :param by: The type of locator to use. Defaults to None.
            :param multi_select: Flag indicating whether the dropdown supports multiple selections. Defaults to False.
            :param single_select: Flag indicating whether the dropdown supports a single selection. Defaults to False.
            :param index: Flag indicating whether selection is based on index (requires single_select=True). Defaults to False.
            :param searchable: Flag indicating whether the dropdown allows searching for options (index and multi select box allows it). Defaults to False.
        """
        self.name = name
        self.by = by
        self.value = self.CONTROL_GROUP.format(value)
        self.is_multi_select = multi_select
        self.is_single_select = single_select
        self.is_searchable = searchable
        self.is_index = index

        self.search_div = (
            self.value + ' [data-test="combo-box"] [data-test="textbox"]'
            if self.is_searchable and self.is_index
            else self.POPOVER + ' [data-test="textbox"]'
        )

        LOGGER.info(
            "Select={} attributes are multi_select={}, single_select={}, index={}, searchable={}, value={}".format(
                name, multi_select, single_select, index, searchable, value
            )
        )

        container = {"base_selector": [None, self.value]}
        super().__init__(driver, container)

        select_common_locator = {
            "values": [None, self.POPOVER + self.VALUES_LOCATOR],
            "search_box": [None, self.search_div],
            "load_values": [None, '[data-test-loading="true"]'],
        }
        self.locator.update_locaters(select_common_locator)
        if self.is_multi_select:
            self._initialize_multi_select()

        if self.is_single_select:
            self._initialize_single_select()

    def _initialize_multi_select(self):
        """
        Initializes the locators for multi-select dropdown.
        """
        self.locator.update_locaters(
            {
                "open": [None, self.value + self.MULTI_BUTTON_LOCATOR],
                "selected": [
                    None,
                    self.value + self.MULTI_SELECTED_LOCATOR,
                ],
                "cancel_selected": [None, self.value + self.DESELECTED],
            }
        )

    def _initialize_single_select(self):
        """
        Initializes the locators for single-select dropdown.
        """

        if self.is_searchable and self.is_index:
            self.single_select_locator = self.value + self.COMBO_BOX
        else:
            self.single_select_locator = self.value + self.SINGLE_BUTTON_LOCATOR

        self.CANCEL_BUTTON_LOCATOR = (
            self.value + self.CANCEL_BUTTON_LOCATOR
            if not self.is_index
            else self.COMBO_BOX + self.CANCEL_BUTTON_LOCATOR
        )

        self.locator.update_locaters(
            {
                self.name: [self.by, self.value],
                "cancel_selected": [None, self.CANCEL_BUTTON_LOCATOR],
                "open": [
                    None,
                    self.value
                    + (self.COMBO_BOX if self.is_index else self.SINGLE_BUTTON_LOCATOR),
                ],
                "selected": [None, self.single_select_locator],
            }
        )

    def select_multiple_values(self, values: list) -> bool:
        """
        Selects multiple values from the dropdown.

            :param values: List of values to be selected.
            :return: True if all values were selected successfully.
        """
        if self.is_multi_select:
            self.deselect_all()
            self.wait_for_element("values")
            for option in self._find_elements(*self.locator.get_locator("values")):
                LOGGER.info("option text: {}".format(option.text))
                for type in values:
                    if option.text.strip().lower() == type.lower():
                        time.sleep(1)
                        option.click()
        return True

    def select(self, value: str, deselect_first: bool = True) -> bool:
        """
        Selects an option from the dropdown.

            :param value: The value to be selected.
            :params deselect_first: Deselect all the selected value of the multi select component.
            :return: True if the value was found and selected.
            :raises ValueError: If the given value is not found in the dropdown options.
        """
        LOGGER.info("Selecting : {}".format(value))
        if self.is_single_select and self.is_index:
            self.deselect()
        elif deselect_first and self.is_multi_select:
            self.deselect_all()

        self.click_element("open")

        if self.is_searchable and not self.is_index:
            self._search(value)

        self.wait_for_element("values")
        for option in self._find_elements(*self.locator.get_locator("values")):
            LOGGER.info("option text: {}".format(option.text))
            if option.text.strip().lower() == value.lower():
                option.click()
                return True

        raise ValueError("Given value={} is not found.".format(value))

    def selected_values(self):
        """
        Retrieves the selected values from the dropdown.

            :return: A list of selected values.
        """
        if self.is_multi_select:
            selected_elements = self._find_elements(
                *self.locator.get_locator("selected")
            )
            return [element.text.strip() for element in selected_elements]
        else:
            element = self.get_element(*self.locator.get_locator("selected"))
            if self.is_index:
                return [element.get_attribute("value")]
            elif element.get_attribute("data-test-value"):
                return [element.get_attribute("label")]
            else:
                return False

    def deselect_all(self) -> bool:
        """
        Deselects all selected options in the multi-select dropdown.

            :return: True if all options were deselected successfully.
            :raises Exception: If an error occurs while deselecting options.
        """
        LOGGER.info("Deselecting all selected options from multi select dropdown.")
        if self.is_multi_select:
            try:
                for element in self._find_elements(
                    *self.locator.get_locator("cancel_selected")
                ):
                    LOGGER.info("element removed: {}".format(element.text))
                    element.click()
                    time.sleep(0.1)
            except Exception as e:
                LOGGER.error(
                    "Error: {}  \n Traceback: {}".format(e, traceback.format_exc())
                )
                self.action.send_keys(Keys.ESCAPE).perform()
                return False

            self.action.send_keys(Keys.ESCAPE).perform()
            return True
        else:
            LOGGER.error("Single select does not have deselect all action.")
            raise ValueError("Single select does not have deselect all action.")

    def deselect(self, value: Optional[str] = None):
        """
        Deselects a specific value in the dropdown.

            :param value: The value to be deselected. Defaults to None.
            :return: True if the value was found and deselected.
            :raises ValueError: If the given value is not found.
        """

        LOGGER.info(f"Deselecting value={value}")
        try:
            if self.is_single_select and not self.is_index:
                self.click_element("cancel_selected")
                return True

            elif self.is_single_select and self.is_index:
                self.wait_for_element_invisible("load_values")
                self.click_element("open")
                self.click_element("cancel_selected")
                self.action.send_keys(Keys.ESCAPE).perform()
                return True

            elif self.is_multi_select and value:
                elements = self._find_elements(
                    *self.locator.get_locator("cancel_selected")
                )
                for element in elements:
                    if element.text.strip().lower() == value.lower():
                        element.click()
                self.action.send_keys(Keys.ESCAPE).perform()
                return True
        except Exception as e:
            LOGGER.error(
                "Error: {}  \n Traceback: {}".format(e, traceback.format_exc())
            )
            return False
        else:
            raise ValueError(f"Given value {value} is not found.")

    def get_all_options(self) -> list:
        """
        Retrieves all options from the dropdown.

            :return: A list of all options in the dropdown.
        """
        if self.is_single_select and self.is_index:
            self.deselect()
        self.click_element("open")
        self.wait_for_element("values")
        val = [
            element.text.strip()
            for element in self._find_elements(*self.locator.get_locator("values"))
        ]

        if self.is_multi_select:
            val.extend(self.selected_values())

        LOGGER.info("All options: {}".format(val))
        return val

    def find_value(self, value: str) -> bool:
        """
        Checks if a value exists in the dropdown.

            :param value: The value to check for.
            :return: True if the value exists, otherwise False.
        """
        return bool([val for val in self.get_all_options() if val == value])

    def search_list(self, value: str) -> list:
        """
        Searches for a value in the dropdown and return the list of searched values.

            :param value: The value to search for.
            :return: A list of search results matching the value.
        """
        val = []
        self.click_element("open")
        self._search(value)
        for option in self._find_elements(*self.locator.get_locator("values")):
            val.append(option.text.strip())

        return val

    def _search(self, value):
        """
        Search the value in select box.
            :params value: A search value to search in select component.
        """
        if self.is_searchable and not self.is_multi_select and self.is_index:
            self.click_element("cancel_selected")
        self.enter_text("search_box", value)
        self.wait_for_element("values")

    def is_editable(self) -> bool:
        """
        Checks if the Select component is editable.

            :return: True if the Select component is editable, False otherwise.
        """
        self.wait_for_element(self.name)
        input_element = self.get_element(*self.locator.get_locator("open"))
        editable = not (
            input_element.get_attribute("disabled")
            or input_element.get_attribute("readonly")
        )
        LOGGER.info("Is element Editable: {}".format(editable))
        return editable
