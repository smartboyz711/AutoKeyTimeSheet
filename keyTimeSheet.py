from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from dataFillClass import data_fill_jira
import defaultData

list_deleted_time_date: list[str] = []
list_tasked_time_date: list[str] = []


def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(argument="start-maximized")
    # Initialize WebDriver
    driver = WebDriver(service=ChromeService(), options=options)
    driver.get(url="https://newtimesheet.aware.co.th/timesheet/Login.aspx")
    return driver


def login_time_entry(driver: WebDriver, username: str, password: str):
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_txtUserName"))
    )
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_txtUserPassword"))
    )
    driver.find_element(By.ID, value="cphContent_txtUserName").send_keys(username)
    driver.find_element(By.ID, value="cphContent_txtUserPassword").send_keys(
        password + Keys.RETURN
    )
    # Wait and find Tab Time Entry
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Time Entry"))
    )
    # Click Tab Time Entry
    driver.find_element(By.LINK_TEXT, value="Time Entry").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContentRight_lblDay"))
    )
    driver.find_element(By.ID, value="cphContentRight_lblDay").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_lblDateShow"))
    )


def __find_fill_datadate(driver: WebDriver, data_fill: data_fill_jira):
    while True:
        # detect date in Calender
        filldatetime = data_fill.filldatetime
        filldate = filldatetime.strftime("%a").upper()
        # get day Monday
        element_mon = driver.find_element(By.ID, value="MON")
        day_mon = element_mon.find_element(
            By.CLASS_NAME, value="day-Num"
        ).get_attribute("textContent")
        month_mon = (
            int(
                element_mon.find_element(
                    # type: ignore
                    By.CLASS_NAME,
                    value="month-Num",
                ).get_attribute("textContent")
            )
            + 1
        )
        year_mon = element_mon.find_element(
            By.CLASS_NAME, value="year-Num"
        ).get_attribute("textContent")
        # get day Sunday
        element_sun = driver.find_element(By.ID, value="SUN")
        day_sun = element_sun.find_element(
            By.CLASS_NAME, value="day-Num"
        ).get_attribute("textContent")
        month_sun = (
            int(
                element_sun.find_element(
                    # type: ignore
                    By.CLASS_NAME,
                    value="month-Num",
                ).get_attribute("textContent")
            )
            + 1
        )
        year_sun = element_sun.find_element(
            By.CLASS_NAME, value="year-Num"
        ).get_attribute("textContent")

        mon_datetime = datetime.strptime(
            f"{day_mon}/{month_mon}/{year_mon}", defaultData.df_string
        )
        sun_datetime = datetime.strptime(
            f"{day_sun}/{month_sun}/{year_sun}", defaultData.df_string
        )

        if mon_datetime <= filldatetime <= sun_datetime:
            filldatetime_str = filldatetime.strftime("%A, %B %d, %Y")
            current_date_str = driver.find_element(
                By.ID, value="cphContent_lblDateShow"
            ).text
            # Check Same Date as last time
            if filldatetime_str != current_date_str:
                driver.find_element(By.ID, value=filldate).click()  # FRI
            WebDriverWait(driver, timeout=defaultData.time_out).until(
                method=EC.text_to_be_present_in_element(
                    locator=(By.ID, "cphContent_lblDateShow"), text_=filldatetime_str
                )
            )  # Friday, October 14, 2022
            break
        elif filldatetime < mon_datetime:
            driver.find_element(By.CLASS_NAME, value="previousWeek").click()
            WebDriverWait(driver, timeout=defaultData.time_out).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "previousWeek"))
            )
        else:
            driver.find_element(By.CLASS_NAME, value="nextWeek").click()
            WebDriverWait(driver, timeout=defaultData.time_out).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "nextWeek"))
            )


def __delete_all_taskdata(driver: WebDriver, data_fill: data_fill_jira):
    date_time_str = data_fill.filldatetime.strftime(defaultData.df_string)
    try:
        driver.find_element(By.ID, value="cphContent_DeleteAll")
    except NoSuchElementException:
        return

    if (
        (float(driver.find_element(By.ID, value="totalHours").text) > 0)
        and (date_time_str not in list_deleted_time_date)
        and (date_time_str not in list_tasked_time_date)
    ):
        driver.find_element(By.ID, value="cphContent_DeleteAll").click()
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.presence_of_element_located((By.ID, "dialog-confirm-delete"))
        )
        driver.find_element(By.XPATH, value="//span[contains(.,'OK')]").click()  # OK
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.invisibility_of_element_located((By.ID, "dialog-confirm-delete"))
        )
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.invisibility_of_element_located((By.ID, "cphContent_DeleteAll"))
        )
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.element_to_be_clickable((By.ID, "cphContent_addTimeEntry"))
        )
        # add time that already deleted in time sheet
        list_deleted_time_date.append(date_time_str)


def __fill_task_data(driver: WebDriver, data_fill: data_fill_jira):
    try:
        driver.find_element(By.ID, value="cphContent_addTimeEntry")
    except NoSuchElementException:
        raise NoSuchElementException(
            msg=f"this Datetime {data_fill.filldatetime.strftime(
            format=defaultData.df_string)} is already submitted"
        )

    driver.find_element(By.ID, value="cphContent_addTimeEntry").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_pnlAddEditTimelist"))
    )
    pnladdedit_timelist = driver.find_element(
        By.ID, value="cphContent_pnlAddEditTimelist"
    )
    driver.find_element(By.ID, value="cphContent_lnkAddTimelist").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element(
            (By.ID, "cphContent_ddlPopCustomer"), data_fill.customer
        )
    )
    Select(
        pnladdedit_timelist.find_element(By.ID, value="cphContent_ddlPopCustomer")
    ).select_by_visible_text(data_fill.customer)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element(
            (By.ID, "cphContent_ddlPopProject"), data_fill.project
        )
    )
    Select(
        pnladdedit_timelist.find_element(By.ID, value="cphContent_ddlPopProject")
    ).select_by_visible_text(data_fill.project)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element(
            (By.ID, "cphContent_ddlPopRole"), data_fill.role
        )
    )
    Select(
        pnladdedit_timelist.find_element(By.ID, value="cphContent_ddlPopRole")
    ).select_by_visible_text(data_fill.role)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element(
            (By.ID, "cphContent_ddlPopTask"), data_fill.task
        )
    )
    Select(
        pnladdedit_timelist.find_element(By.ID, value="cphContent_ddlPopTask")
    ).select_by_visible_text(data_fill.task)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.element_to_be_clickable((By.ID, data_fill.get_id_billtype()))
    )
    pnladdedit_timelist.find_element(By.ID, value=data_fill.get_id_billtype()).click()
    pnladdedit_timelist.find_element(By.ID, value="cphContent_txtHours").send_keys(
        str(data_fill.hours)
    )
    pnladdedit_timelist.find_element(By.ID, value="cphContent_rdlInternal2").click()
    pnladdedit_timelist.find_element(
        By.ID, value="cphContent_txtInternalDescription"
    ).send_keys(data_fill.description_str())
    driver.find_element(By.XPATH, value="//span[contains(.,'Save')]").click()  # save
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.invisibility_of_element_located((By.ID, "cphContent_pnlAddEditTimelist"))
    )
    date_time_str = data_fill.filldatetime.strftime(defaultData.df_string)
    # add time that already add to time sheet
    list_tasked_time_date.append(date_time_str)


def __submit_time_sheet(driver: WebDriver):
    try:
        phcontent_btnsubmitlist = driver.find_element(
            By.ID, value="cphContent_btnSubmitList"
        )
    except NoSuchElementException:
        return

    element_mon = driver.find_element(By.ID, value="MON")
    color_mon = element_mon.find_element(By.CLASS_NAME, value="icon-ok").get_attribute(
        "style"
    )
    element_tue = driver.find_element(By.ID, value="TUE")
    color_tue = element_tue.find_element(By.CLASS_NAME, value="icon-ok").get_attribute(
        "style"
    )
    element_wed = driver.find_element(By.ID, value="WED")
    color_wed = element_wed.find_element(By.CLASS_NAME, value="icon-ok").get_attribute(
        "style"
    )
    element_thu = driver.find_element(By.ID, value="THU")
    color_thu = element_thu.find_element(By.CLASS_NAME, value="icon-ok").get_attribute(
        "style"
    )
    element_fri = driver.find_element(By.ID, value="FRI")
    color_fri = element_fri.find_element(By.CLASS_NAME, value="icon-ok").get_attribute(
        "style"
    )

    if (
        color_mon in [defaultData.orange, defaultData.green]
        and color_tue in [defaultData.orange, defaultData.green]
        and color_wed in [defaultData.orange, defaultData.green]
        and color_thu in [defaultData.orange, defaultData.green]
        and color_fri in [defaultData.orange, defaultData.green]
    ):
        phcontent_btnsubmitlist.click()
        driver.switch_to.frame(0)
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.element_to_be_clickable((By.ID, "cphContent_btnSave"))
        )
        driver.find_element(By.ID, value="cphContent_btnSave").click()
        driver.switch_to.default_content()
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.invisibility_of_element_located((By.ID, "cphContent_btnSubmitList"))
        )


def main_filldatatask(
    driver: WebDriver, data_fill_list: list[data_fill_jira]
) -> list[data_fill_jira]:
    for data_fill in data_fill_list:
        if not data_fill.status_message and data_fill.filldatetime > datetime.min:
            try:
                __find_fill_datadate(driver, data_fill)
                __delete_all_taskdata(driver, data_fill)
                __fill_task_data(driver, data_fill)
            except Exception as e:
                data_fill.status_message = str(e)
    list_deleted_time_date.clear()
    list_tasked_time_date.clear()
    return data_fill_list


def main_submitatask(
    driver: WebDriver, data_fill_list: list[data_fill_jira]
) -> list[data_fill_jira]:
    for data_fill in data_fill_list:
        try:
            __find_fill_datadate(driver, data_fill)
            __submit_time_sheet(driver)
        except Exception as e:
            data_fill.status_message = (
                f"{data_fill.status_message} | Submit Error : {str(e)}"
            )
    return data_fill_list
