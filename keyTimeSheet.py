from datetime import date, datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from dataFillClass import Data_fill
import defaultData


def get_driver() -> WebDriver:
    # set option to make browsing easier
    option = webdriver.ChromeOptions()
    # option.add_argument("disable-infobars")
    option.add_argument("start-maximized")
    # option.add_argument("disable-dev-shm-usage")
    # option.add_argument("no-sandbox")
    # option.add_experimental_option(
    # name="excludeSwitches", value=["enable-automation"])
    # option.add_argument("disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=option)
    driver.get("https://newtimesheet.aware.co.th/timesheet/Login.aspx")
    # driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    return driver


def login_timeEntry(driver: WebDriver, username: str, password: str):
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_txtUserName")))
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_txtUserPassword")))
    driver.find_element(
        By.ID, value="cphContent_txtUserName").send_keys(username)
    driver.find_element(By.ID, value="cphContent_txtUserPassword").send_keys(
        password + Keys.RETURN)
    # Wait and find Tab Time Entry
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Time Entry")))
    # Click Tab Time Entry
    driver.find_element(By.LINK_TEXT, value="Time Entry").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContentRight_lblDay")))
    driver.find_element(By.ID, value="cphContentRight_lblDay").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_lblDateShow")))


def find_fillDataDate(driver: WebDriver, data_fill: Data_fill):
    while True:
        # detect date in Calender
        filldatetime = data_fill.filldatetime
        filldate = filldatetime.strftime("%a").upper()
        if (filldate == "SAT" or filldate == "SUN"):
            raise Exception("Can't fill Time Sheet on Saturday and Sunday")
        # get day Monday
        elementMon = driver.find_element(By.ID, value="MON")
        dayMon = elementMon.find_element(
            By.CLASS_NAME, value="day-Num").get_attribute("textContent")
        monthMon = int(elementMon.find_element(
            # type: ignore
            By.CLASS_NAME, value="month-Num").get_attribute("textContent"))+1
        yearMon = elementMon.find_element(
            By.CLASS_NAME, value="year-Num").get_attribute("textContent")
        # get day Sunday
        elementSun = driver.find_element(By.ID, value="SUN")
        daySun = elementSun.find_element(
            By.CLASS_NAME, value="day-Num").get_attribute("textContent")
        monthSun = int(elementSun.find_element(
            # type: ignore
            By.CLASS_NAME, value="month-Num").get_attribute("textContent"))+1
        yearSun = elementSun.find_element(
            By.CLASS_NAME, value="year-Num").get_attribute("textContent")

        monDateTime = datetime.strptime(
            f"{dayMon}/{monthMon}/{yearMon}", defaultData.df_string)
        sunDateTime = datetime.strptime(
            f"{daySun}/{monthSun}/{yearSun}", defaultData.df_string)

        if (monDateTime <= filldatetime <= sunDateTime):
            filldatetime_str = filldatetime.strftime("%A, %B %d, %Y")
            current_date_str = driver.find_element(
                By.ID, value="cphContent_lblDateShow").text
            # Check Same Date as last time
            if (filldatetime_str != current_date_str):
                driver.find_element(By.ID, value=filldate).click()  # FRI
            WebDriverWait(driver, timeout=defaultData.time_out).until(EC.text_to_be_present_in_element
                                                                      ((By.ID, "cphContent_lblDateShow"),
                                                                       filldatetime_str))  # Friday, October 14, 2022
            break
        elif (filldatetime < monDateTime):
            driver.find_element(By.CLASS_NAME, value="previousWeek").click()
            WebDriverWait(driver, timeout=defaultData.time_out).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "previousWeek")))
            continue
        else:
            driver.find_element(By.CLASS_NAME, value="nextWeek").click()
            WebDriverWait(driver, timeout=defaultData.time_out).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "nextWeek")))
            continue


def delete_allTaskData(driver: WebDriver):
    try:
        driver.find_element(By.ID, value="cphContent_DeleteAll")
    except NoSuchElementException:
        return

    if (float(driver.find_element(By.ID, value="totalHours").text) > 0):
        driver.find_element(By.ID, value="cphContent_DeleteAll").click()
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.presence_of_element_located((By.ID, "dialog-confirm-delete")))
        driver.find_element(
            By.XPATH, value="//span[contains(.,'OK')]").click()  # OK
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.invisibility_of_element_located((By.ID, "dialog-confirm-delete")))
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.invisibility_of_element_located((By.ID, "cphContent_DeleteAll")))


def fill_taskData(driver: WebDriver, data_fill: Data_fill):
    try:
        driver.find_element(By.ID, value="cphContent_addTimeEntry")
    except NoSuchElementException:
        raise Exception(f"this Datetime {data_fill.filldatetime.strftime(
            defaultData.df_string)} is already submitted")

    driver.find_element(By.ID, value="cphContent_addTimeEntry").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.presence_of_element_located((By.ID, "cphContent_pnlAddEditTimelist")))
    pnlAddEditTimelist = driver.find_element(
        By.ID, value="cphContent_pnlAddEditTimelist")
    driver.find_element(By.ID, value="cphContent_lnkAddTimelist").click()
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element((By.ID, "cphContent_ddlPopCustomer"), data_fill.customer))
    Select(pnlAddEditTimelist.find_element(
        By.ID, value="cphContent_ddlPopCustomer")).select_by_visible_text(data_fill.customer)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element((By.ID, "cphContent_ddlPopProject"), data_fill.project))
    Select(pnlAddEditTimelist.find_element(
        By.ID, value="cphContent_ddlPopProject")).select_by_visible_text(data_fill.project)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element((By.ID, "cphContent_ddlPopRole"), data_fill.role))
    Select(pnlAddEditTimelist.find_element(
        By.ID, value="cphContent_ddlPopRole")).select_by_visible_text(data_fill.role)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.text_to_be_present_in_element((By.ID, "cphContent_ddlPopTask"), data_fill.task))
    Select(pnlAddEditTimelist.find_element(
        By.ID, value="cphContent_ddlPopTask")).select_by_visible_text(data_fill.task)
    WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.element_to_be_clickable((By.ID, data_fill.get_id_billtype())))
    pnlAddEditTimelist.find_element(
        By.ID, value=data_fill.get_id_billtype()).click()
    pnlAddEditTimelist.find_element(
        By.ID, value="cphContent_txtHours").send_keys(data_fill.hours)
    # pnlAddEditTimelist.find_element(
    #    By.ID, value="cphContent_rdlInternal1").click()
    # Select(pnlAddEditTimelist.find_element(
    #    By.ID, value="cphContent_ddlInternalDescription")).select_by_visible_text(data_fill.task)
    pnlAddEditTimelist.find_element(
        By.ID, value="cphContent_rdlInternal2").click()
    pnlAddEditTimelist.find_element(By.ID, value="cphContent_txtInternalDescription").send_keys(
        data_fill.description.__str__())
    driver.find_element(
        By.XPATH, value="//span[contains(.,'Save')]").click()  # save
    WebDriverWait(driver, timeout=defaultData.time_out).until(
        EC.invisibility_of_element_located((By.ID, "cphContent_pnlAddEditTimelist")))


def submit_timeSheet(driver: WebDriver):
    try:
        phContent_btnSubmitList = driver.find_element(
            By.ID, value="cphContent_btnSubmitList")
    except NoSuchElementException:
        return

    elementMon = driver.find_element(By.ID, value="MON")
    colorMon = elementMon.find_element(
        By.CLASS_NAME, value="icon-ok").get_attribute("style")
    elementTue = driver.find_element(By.ID, value="TUE")
    colorTue = elementTue.find_element(
        By.CLASS_NAME, value="icon-ok").get_attribute("style")
    elementWed = driver.find_element(By.ID, value="WED")
    colorWed = elementWed.find_element(
        By.CLASS_NAME, value="icon-ok").get_attribute("style")
    elementThu = driver.find_element(By.ID, value="THU")
    colorThu = elementThu.find_element(
        By.CLASS_NAME, value="icon-ok").get_attribute("style")
    elementFri = driver.find_element(By.ID, value="FRI")
    colorFri = elementFri.find_element(
        By.CLASS_NAME, value="icon-ok").get_attribute("style")

    if (colorMon in [defaultData.orange, defaultData.green]
            and colorTue in [defaultData.orange, defaultData.green]
            and colorWed in [defaultData.orange, defaultData.green]
            and colorThu in [defaultData.orange, defaultData.green]
            and colorFri in [defaultData.orange, defaultData.green]):

        phContent_btnSubmitList.click()
        driver.switch_to.frame(0)
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.element_to_be_clickable((By.ID, "cphContent_btnSave")))
        driver.find_element(By.ID, value="cphContent_btnSave").click()
        driver.switch_to.default_content()
        WebDriverWait(driver, timeout=defaultData.time_out).until(
            EC.invisibility_of_element_located((By.ID, "cphContent_btnSubmitList")))


def main_fillDataTask(driver: WebDriver, data_fill_list: list[Data_fill]) -> list[Data_fill]:
    #prev_datetime: date = date.min
    for data_fill in data_fill_list:
        if (not data_fill.statusMessage):
            try:
                find_fillDataDate(driver, data_fill)
                # if(prev_datetime != data_fill.filldatetime.date()) :
                #    delete_allTaskData(driver)
                #    prev_datetime = data_fill.filldatetime.date()
                fill_taskData(driver, data_fill)
            except Exception as e:
                data_fill.statusMessage = str(e)
    return data_fill_list


def main_submitTask(driver: WebDriver, data_fill_list: list[Data_fill]) -> list[Data_fill]:
    for data_fill in data_fill_list:
        try:
            find_fillDataDate(driver, data_fill)
            submit_timeSheet(driver)
        except Exception as e:
            data_fill.statusMessage = f"{
                data_fill.statusMessage} | Submit Error : {str(e)}"
    return data_fill_list
