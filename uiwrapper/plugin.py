import os
import platform
import sys
import traceback

import allure
import pytest
from allure_commons.types import AttachmentType
from selenium.common.exceptions import WebDriverException

from uiwrapper.helper import RestHandlerHelper, WebDriverHelper
from uiwrapper.log.logging import Logger

LOGGER = Logger.get_logger("uiwrapper")


def pytest_addoption(parser):
    """
    Adds custom command-line options to the pytest parser.

        :params parser: The argument parser instance.
    """
    LOGGER.info("Initializing pytest options.")
    parser.addoption(
        "--browser",
        action="store",
        help="Browser to run UI tests: chrome, edge, firefox",
    )
    parser.addoption(
        "--retry",
        action="store",
        default=3,
        type=int,
        help="Retry count for running the UI tests",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Run tests in headless mode (without user interface)",
    )
    parser.addoption("--splunk-username", action="store", help="Splunk username")
    parser.addoption("--splunk-password", action="store", help="Splunk password")
    parser.addoption(
        "--splunk-web-uri",
        action="store",
        help="Splunk web URI",
        default="http://127.0.0.1:8000",
    )
    parser.addoption(
        "--splunk-rest-uri",
        action="store",
        help="Splunk rest URI",
        default="http://127.0.0.1:8089",
    )
    parser.addoption(
        "--scope",
        action="store",
        help="Scope of the test case (eg. function, session)",
        default="function",
    )
    parser.addoption(
        "--run-local",
        action="store_true",
        default=False,
        help="Run tests marked with 'local'",
    )


def pytest_collection_modifyitems(config, items):
    """
    Filters test items based on the --run-local option.
    If the --run-local option is provided, tests marked with 'local' will be included else skipped.
        :params config: Pytest configuration object used to access command-line options.
        :params items: List of collected test items to be filtered.
    """
    run_local = config.getoption("--run-local")
    if run_local:
        return
    else:
        skip_local = pytest.mark.skip(
            reason="Skipping local tests (use --run-local to include them)"
        )
        for item in items:
            if "local" in item.keywords:
                LOGGER.debug(f"Skipping test: {item.nodeid}")
                item.add_marker(skip_local)


class Config:
    """
    Configuration class for storing test settings.

    Attributes:
        browser (str): The browser to use for testing.
        headless (bool): Whether to run tests in headless mode.
        retry (int): Number of retries for tests.
        splunk (dict): Dictionary containing Splunk connection information.
    """

    def __init__(self, browser, headless, retry, splunk) -> None:
        """
        Initializes the Config object.

            :param browser (str): The browser to use for testing.
            :param headless (bool): Whether to run tests in headless mode.
            :param retry (int): Number of retries for tests.
            :param splunk (dict): Dictionary containing Splunk connection information.
        """
        LOGGER.info("Initializing Config.")
        self._browser = browser
        self._headless = headless
        self._retry = retry
        self._splunk = splunk


@pytest.fixture(scope="session")
def config(request):
    """
    Pytest fixture to create a Config object from command-line options.

        :param request (SubRequest): The request object for accessing command-line options.
        :returns Config: The configuration object with settings for the test session else raise the value error if required options are missing or invalid.

    """
    try:
        browser = request.config.getoption("--browser")
        if not browser:
            raise ValueError("Browser is required. Please specify --browser option.")

        headless = request.config.getoption("--headless")
        retry = int(request.config.getoption("--retry"))
        splunk = {
            "splunk_username": request.config.getoption("--splunk-username"),
            "splunk_password": request.config.getoption("--splunk-password"),
            "splunk_web_uri": request.config.getoption("--splunk-web-uri"),
            "splunk_rest_uri": request.config.getoption("--splunk-rest-uri"),
        }

        return Config(browser=browser, headless=headless, retry=retry, splunk=splunk)
    except Exception as e:
        LOGGER.error(
            "Error in config fixture: {}"
            "\nTraceback: {}".format(e, traceback.format_exc())
        )
        raise


def get_scope(fixture_name, config):
    if config.getoption("--scope") is None:
        return "function"
    elif config.getoption("--scope") == "module":
        return "module"
    elif config.getoption("--scope") == "class":
        return "class"
    return "session"


@pytest.fixture(scope=get_scope)
def selenium_helper(config):
    """
    Pytest fixture to create a WebDriverHelper instance.

        :params config (Config): The configuration object for the test session.
        :Yields WebDriverHelper: The WebDriverHelper instance for managing WebDriver actions.
    """
    exe = Exception()
    for _try in range(config._retry):
        try:
            splunk_driver_helper = WebDriverHelper(config)
            break
        except Exception as e:
            exe = e
            LOGGER.warning(
                "Unable to initialize web driver or login to Splunk instance - Attempt: {} \nTraceback: {}".format(
                    _try, traceback.format_exc()
                )
            )
    else:
        LOGGER.error(
            "Unable to initialize web driver or login to Splunk instance \nTraceback: {}".format(
                traceback.format_exc()
            )
        )
        raise exe

    yield splunk_driver_helper
    LOGGER.info("Closing splunk_driver_helper instance.")
    splunk_driver_helper.driver.quit()


@pytest.fixture(scope="session")
def rest_helper(config):
    """ """
    exe = Exception()
    for _try in range(config._retry):
        try:
            rest_helper = RestHandlerHelper(config)
            break
        except Exception as e:
            exe = e
            LOGGER.warning(
                "Unable to Connect with Splunk instance - Attempt: {} \nTraceback: {}".format(
                    _try, traceback.format_exc()
                )
            )
    else:
        LOGGER.error(
            "Unable to Connect with Splunk Management instance \nTraceback: {}".format(
                traceback.format_exc()
            )
        )
        raise exe
    yield rest_helper


@pytest.fixture(autouse=True)
def log_on_failure(request, selenium_helper):
    yield
    try:
        item = request.node
        if item.rep_call.failed:
            name = item.nodeid.split("::")[-1]
            allure.attach(
                selenium_helper.driver.get_screenshot_as_png(),
                name=name,
                attachment_type=AttachmentType.PNG,
            )
        elif item.rep_setup.failed:
            allure.attach(
                selenium_helper.driver.get_screenshot_as_png(),
                name="login_error",
                attachment_type=AttachmentType.PNG,
            )
    except Exception as e:
        LOGGER.warning(
            "Got exception while making test report: {}\n Traceback: {}".format(
                e, traceback.format_exc()
            )
        )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Generate the test case report.

    :param item (Object): The test item object, representing the test function or method.
        It contains information about the test, such as its name, location, and metadata
    :param call (Object): The CallInfo object, which contains information about the test call,
        including when it was made, its outcome (e.g., passed, failed, skipped),
    """
    LOGGER.debug("pytest_runtest_makereport: Start generating allure report")
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture(scope="session", autouse=True)
def generate_environment_properties(config):
    try:
        env_details = {
            "browser": config._browser,
            "os_platform": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "python_version": sys.version.replace("\n", ""),
        }
        with open("environment.properties", "w") as f:
            for key, value in env_details.items():
                f.write(f"{key} = {value}\n")
    except Exception as e:
        LOGGER.error(
            "Got exception while creating environment properties for allure reports: {}".format(
                e
            )
        )
