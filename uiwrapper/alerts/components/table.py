import time
import traceback
from typing import Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from uiwrapper.alerts.components.alert_base import AlertBaseComponent
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


class AlertTable(AlertBaseComponent):
    ROWS = " tr.list-item.savedsearches-gridrow"
    COLS = " td.cell-{}"
    COLS_NO = " td:nth-child({})"
    EDIT_BUTTON = ".edit-alert"
    ENABLE_DISABLE = ".enable-disable"
    CLONE_BUTTON = "a.clone"
    MOVE_BUTTON = "a.move"
    SEARCH_BUTTON = ' [data-name="nameFilter"] input.search-query'
    DELETE_POPUP = " div.deletePrompt"
    DELETE_BUTTON = " a.delete"
    DELETE_CANCEL = ".modal-btn-cancel"
    DELETE_CLOSE = ".modal-dialog button.close"
    CLEAR_FILTER = "a.control-clear"
    ALERT_KEY = ' [data-test="alert-icon"]'
    SWITCH_PAGE = " .pull-right li a"

    # WAIT_FOR = '[data-test="table"]'

    def __init__(self, driver, container: dict) -> None:
        """
        Initializes the Table object with given parameters.

            :param driver: WebDriver: instance to interact with the web page.
            :param container:  by and value containing dict to locate table container.
        """
        self.name = list(container)[0]
        self.value = container[self.name][1]
        super().__init__(driver, container)

        new_locator = {
            "input_number": [None, self.value + " .shared-collectioncount"],
            "status_column": [None, ' [data-test="status"]'],
            "clear_filter": [None, ' [data-test="clear"]'],
            "search_box": [None, ' [data-name="nameFilter"] input.search-query'],
            "loader": [None, self.value + ' [data-test="wait-spinner"]'],
            "popup": [None, "div.deletePrompt"],
            "clone_btn": [None, "a.clone"],
            "edit_btn": [None, ".edit-alert"],
            "delete_btn": [None, "a.delete"],
            "status_button": [None, ' [data-test="button"][role="switch"]'],
            "switch_to_page": [None, self.value + self.SWITCH_PAGE],
            "main_table": [None, 'table[data-test="main-table"]'],
            "table_head": [None, ' [data-test="head"]'],
            "table_headers": [None, self.value + " th"],
            "table_container": [None, self.value + ' [data-test="table"]'],
            "expand": [None, '[data-test="expand"]'],
            "rows": [None, self.value + self.ROWS],
        }
        self.locator.update_locaters(new_locator)

    def get_list_of_rows(self, rows: Optional[list] = None) -> list:
        """
        Retrieves a list of all rows in the table.

            :params rows: Existing list of rows. Defaults to None.
            :return: List of WebElement representing rows in the table.
        """
        self.wait_for_element("table_container")
        if rows is None:
            rows = []

        current_rows = self._find_elements(*self.locator.get_locator("rows"))
        rows.extend(current_rows)

        if self.next_page():
            return self.get_list_of_rows(rows)

        return rows

    def get_total_rows_elements(self):
        """
        Generator function to yield all row elements in the table.

            :yields web element: Each row element in the table.
        """
        self.wait_for_element("table_container")
        elements = self._find_elements(*self.locator.get_locator("rows"))
        yield from elements
        if self.next_page():
            yield from self.get_total_rows_elements()

    def get_row(self, value: str, column: str = "name", is_search: bool = False):
        """
        Retrieves a specific row element based on given value and column.

            :param value (str): Value to search within the specified column.
            :param column (str, optional): Column name to search in. Defaults to "name".
            :param is_search (bool, optional): Whether the search is specifically filtered. Defaults to False.
            :return: WebElement: Found row element or raise error If no matching row is found.

        """
        self.wait_for_element("table_container")
        elements = self.get_total_rows_elements()
        for row in elements:
            if is_search:
                LOGGER.info("For Search")
                if value in self._column_value(row, column):
                    return row
            elif self._column_value(row, column) == value:
                return row
        else:
            raise ValueError("{} row not found in table".format(value))

    def get_rows_count(self) -> int:
        """
        Retrieves the total count of rows in the table.
        """

        count = len(self.get_list_of_rows())
        return count

    def get_expanded_row_value(self, input_name: str) -> dict:
        """
        Retrieves a expanded row values for specific row from table.

            :param input_name (str): Value to search within the specified column.
            :return: dict: return combination of key and value of the input configuration.
                eg: {  input_name: name,
                        index: main,
                    }

        """
        LOGGER.info("Expanding row: {}".format(input_name))
        expand_row = self.get_row(input_name)
        expand_btn = expand_row.find_element(*self.locator.get_locator("expand"))
        expand_btn.click()
        self.wait_for_element("expanded_row")
        terms = [
            element.text.strip()
            for element in self._find_elements(
                *self.locator.get_locator("expanded_row_term")
            )
        ]
        description = [
            element.text.strip()
            for element in self._find_elements(
                *self.locator.get_locator("expanded_row_desc")
            )
        ]
        return dict(zip(terms, description))

    def delete_row(self, input_name: str, action: Optional[str] = None):
        """
        Deletes a row from the table based on the input name.
            :param action: which action we want to perform on the delete popup.
                - for cancel the delete use "cancel"
                - for close the delete use "close"
                - for delete row the use "delete"
        """
        try:
            self.wait_for_element("table_container")
            LOGGER.info("Deleting input: {}".format(input_name))
            del_row = self.get_row(input_name)
            del_btn = del_row.find_element(*self.locator.get_locator("delete_btn"))
            del_btn.click()
            self.wait_for_element("popup")
            if action == "delete":
                self.delete_btn.click()
            elif action == "close":
                self.close()
            elif action == "cancel":
                self.cancel()
            else:
                LOGGER.warning(
                    "Opening and closing the pop to read the conformation message."
                )
                time.sleep(2)
                self.cancel()
            self.wait_for_element_invisible("popup")
            return True
        except Exception as e:
            LOGGER.error(
                "Unable to perform action:{} error: {}\nTraceback: {}".format(
                    action, e, traceback.format_exc()
                )
            )
            return False

    def edit_row(self, input_name: str):
        """
        Edits a row in the table based on the input name.
        """
        self.wait_for_element("table_container")
        LOGGER.info("Editing input: {}".format(input_name))
        edit_row = self.get_row(input_name)
        edit_btn = edit_row.find_element(*self.locator.get_locator("edit_btn"))
        edit_btn.click()
        self.wait_for_element("open_modal")

    def clone_row(self, input_name: str):
        """
        Clones a row in the table based on the input name.

            :param input_name: The name of the row to clone.
        """
        self.wait_for_element("table_container")
        LOGGER.info("Cloning input: {}".format(input_name))
        clone_row = self.get_row(input_name)
        clone_btn = clone_row.find_element(*self.locator.get_locator("clone_btn"))
        clone_btn.click()
        self.wait_for_element("open_modal")

    def get_column_list(self, column: str):
        """
        Retrieves a list of values from a specified column in all rows.

            :param column: The column name to retrieve values from.
            :return: A list of values from the specified column.
        """
        cols = []
        for row in self.get_total_rows_elements():
            cols.append(self._column_value(row, column))
        return cols

    def get_column_value(self, row: str, column: str):
        """
        Return the specific column value from the table
            :params row: The name of the row to get column value
            :params column: The name of the column to get value.
            :return: A String containing the value of the column.
        """
        return self._column_value(self.get_row(row), column)

    def _column_value(self, row, column: str):
        """
        Retrieves the value of a specified column for a given row.

            :param row: The WebElement representing the row.
            :param column: The column name to retrieve the value from.
            :return: The value of the specified column for the given row.
        """
        LOGGER.info("Getting column value for row={} and column={}".format(row, column))
        self.wait_for_element("table_container")
        column = column.lower().replace(" ", "_")
        if column == "status":
            column_value = self._find_element(row, "status_column").text.strip()
        else:
            temp_col = {"temp_col": [None, self.value + self.COLS.format(column)]}
            self.locator.update_locaters(temp_col)
            column_value = self.get_element_text(self._find_element(row, "temp_col"))
        return column_value

    def search(self, search: str):
        """
        Performs a search operation in the table.

            :param search: The string to search for.
            :return: A list of WebElement objects representing rows matching the search criteria.
        """
        self.wait_for_element("table_container")
        LOGGER.info("Searching with search string: {}".format(search))
        self.enter_text("search_box", search)
        self._wait_to_be_stale(
            self._find_elements(*self.locator.get_locator("rows"))[0]
        )
        rows = self.get_list_of_rows()
        return rows

    def clear_search(self):
        """Clears the search box in the table."""
        self.wait_for_element("table_container")
        self.enter_text("search_box", "test text")
        self.wait_for_element_clickable("clear_filter")
        self.click_element("clear_filter")

    def next_page(self):
        """
        Moves to the next page in the table pagination.

            :return: True if successfully navigated to the next page, otherwise False.
            :raises ValueError: If the next page element is not found.
        """
        self.wait_for_element("table_container")
        time.sleep(10)
        elements = self.driver.find_elements(
            *self.locator.get_locator("switch_to_page")
        )
        if elements:
            for page in elements:
                if self.get_element_text(page).lower() == "next":
                    try:
                        if self._is_element_clickable(page):
                            page.click()
                            return True
                        return False
                    except Exception as e:
                        LOGGER.warning("Unexpected error occurred: {}".format(e))
                        return False
            else:
                raise ValueError("page: {} is not found.".format(page))
        return False

    def prev_page(self):
        """
        Moves to the previous page in the table pagination.

            :return: True if successfully navigated to the previous page, otherwise False.
            :raises ValueError: If the previous page element is not found.
        """
        self.wait_for_element("table_container")
        elements = self._find_elements(*self.locator.get_locator("switch_to_page"))
        if elements:
            for page in elements:
                if self.get_element_text(page).lower() == "prev":
                    try:
                        if self._is_element_clickable(page):
                            page.click()
                            return True
                        return False
                    except Exception as e:
                        LOGGER.warning("Unexpected error occurred: {}".format(e))
                        return False
            else:
                raise ValueError("page: {} is not found.".format(page))
        return False

    def switch_to(self, value: str):
        """
        Switches to a specific page in the table pagination.

            :param value: The label of the page to switch to.
            :return: True if successfully switched to the specified page, otherwise False.
            :raises ValueError: If the specified page label is not found.
        """
        self.wait_for_element("table_container")
        time.sleep(5)
        elements = self._find_elements(*self.locator.get_locator("switch_to_page"))
        if elements:
            for page in elements:
                if self.get_element_text(page).lower() == value.lower():
                    try:
                        if self._is_element_clickable(page):
                            page.click()
                            return True
                        return False
                    except Exception as e:
                        LOGGER.warning("Unexpected error occurred: {}".format(e))
                        return False
            else:
                raise ValueError("page: {} is not found.".format(page))
        return False

    def get_input_count(self):
        """
        Retrieves the total count of configured inputs.

            :return: The total count of configured inputs.
        """
        ele = self.get_element(*self.locator.get_locator("input_number"))
        count = self.get_element_text(ele)
        LOGGER.info("Total Configure count: {}".format(count))
        return count

    def sort_table(self, column: str = "name", order: str = "asc"):
        """
        Sorts the table by the specified column and order.

            :param column: The name of the column to sort by. Defaults to "name".
            :param order: Sorting order, either "asc" (ascending) or "desc" (descending). Defaults to "asc".
            :return: True if sorting is successful, otherwise raises a ValueError.
        """
        LOGGER.info("Sorting table with column: {} and order: {}".format(column, order))
        self.wait_for_element("table_head")
        for th in self._find_elements(*self.locator.get_locator("table_headers")):
            LOGGER.info("Th in sort: {}".format(th.text.lower()))
            if th.text != "" and (th.text.lower() == column.lower()):
                LOGGER.info("Sorting")
                current_sort_order = th.get_attribute("data-test-sort-dir")
                if (order == "asc" and current_sort_order == "asc") or (
                    order == "desc" and current_sort_order == "desc"
                ):
                    LOGGER.info("Already sorted.")
                    return True
                elif (order == "asc" and current_sort_order == "desc") or (
                    order == "desc" and current_sort_order == "asc"
                ):
                    th.click()
                    time.sleep(0.1)
                    return True
                else:
                    time.sleep(2)
                    th.click()
                    time.sleep(2)
                    if order == "desc":
                        th.click()
                        return True
        else:
            raise ValueError("Failed to sort the {}".format(column))

    def get_headers(self) -> list:
        """
        Retrieves the headers of the table.

            :return: A list of header names in the table.
        """
        headers = []
        self.wait_for_element("table_head")
        for th in self._find_elements(*self.locator.get_locator("table_headers")):
            LOGGER.info("get headers: {}".format(th.text))
            if th.text != "":
                headers.append(th.text.strip())
        LOGGER.info("Available headers: {}".format(headers))
        return headers

    def update_status(self, input_name: str, enable: bool = False):
        """
        Toggles the status of a row in the table.

            :param input_name: The name of the row to toggle.
            :param enable: Whether to enable (`True`) or disable (`False`) the row. Defaults to False.
            :raises Exception: If the input is already enabled when trying to enable it again.
        """
        status_row = self.get_row(input_name)
        status_label = (
            self._find_element(status_row, "status_column").text.strip().lower()
        )
        LOGGER.info("Status label: {}".format(status_label))
        if (status_label != "enabled" and enable) or (
            status_label == "enabled" and not enable
        ):
            status_button = self._find_element(status_row, "status_button")
            status_button.click()
            return

        return

    def _is_element_clickable(self, element):
        """
        Checks if an element is clickable.

            :param element: The WebElement to check.
            :return: True if the element is clickable, otherwise False.
        """
        try:
            LOGGER.info("Checking if the next page is clickable.")
            if element.is_displayed() and element.is_enabled():
                return True
        except Exception as e:
            LOGGER.error("Next page button is not clickable.\n Error: {}".format(e))
            return False
        return False

    def _wait_to_be_stale(self, element):
        """
        Waits for an element to become stale in the DOM.

            :param element: The WebElement to wait for.
            :return: True if the element became stale, otherwise False.
        """
        try:
            self.wait.until(EC.staleness_of(element))
            return True
        except TimeoutException:
            LOGGER.warning("Timeout exception.")
            pass
