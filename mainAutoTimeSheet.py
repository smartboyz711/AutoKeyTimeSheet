from datetime import datetime
import os
from typing import List
import pandas as pd
from pandas import DataFrame
import convertJiraToList as cjtl
import jitaClockWork as jcw
from jitaClockWork import jira_clockwork
from dataFillClass import data_fill_jira
import keyTimeSheet as kt
from selenium.webdriver.chrome.webdriver import WebDriver
import input_autoTimeSheet as iat


def main():
    try:
        jira_df: DataFrame = jcw.read_and_combine_excel_files(
            folder_path=iat.folder_path
        )
        list_jira_clockwork: List[jira_clockwork] = (
            jcw.convert_dataframe_to_jira_clockwork(df=jira_df)
        )

        if list_jira_clockwork :
            data_fill_list: list[data_fill_jira] = cjtl.convert_jira_to_list(
                list_jitaclockwork=list_jira_clockwork
            )
            driver: WebDriver = kt.get_driver()
            kt.login_time_entry(driver, iat.username_aware, password=iat.password_aware)
            data_fill_list = kt.main_filldatatask(driver, data_fill_list)

            df_data_fill = pd.DataFrame([x.as_dict() for x in data_fill_list])

            # gen report
            start_time = datetime.now()
            date_today = start_time.strftime("%d%m%Y_%H%M%S")
            filename_report = f"Aware_time_sheet_report_{date_today}.xlsx"
            pathname = "Report"
            # Create Path
            os.makedirs(pathname, exist_ok=True)

            outputdir = f"{pathname}/{filename_report}"
            df_data_fill.to_excel(excel_writer=outputdir, index=False)

            print("fill time Sheet Success you can check result ==> " + outputdir)
            driver.close()

    except Exception as e:
        print(f"An error occurred Cannot Key time sheet. : {e})")
